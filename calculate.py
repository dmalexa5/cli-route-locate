import tomllib

# Load config file
with open('config.toml', 'rb') as f:
    config = tomllib.load(f)

def laser(thickness:float, grade:str, perimeter:float) -> float:
    '''Calculates the usage for the laser cell. 
    Handles both fiber and plasma laser usage.'''
    
    if type(thickness) == str:
        thickness = float(thickness)
    
    if type(perimeter) == str:
        perimeter = float(perimeter)

    thickness = round(thickness, 3)
    
    # Get the available cutting speeds
    speeds = []
    for key in config['laser'].keys():
        system = config['laser'][key]
        
        # find the system (i.e. 4k CO2) speed
        for setting in system:
            
            # Check if thickness matches and grade is cuttable
            if setting[0] == thickness and grade in setting[2]:
                speeds.append(setting[1])

                break
    
    # Check if thickness and grade are valid
    if sum(speeds) == 0: 
        raise UsageError(f'Unable to calculate usage for thickness {thickness} and grade {grade}')
    else:
        # Calculate usage
        usage = sum([(perimeter / speed) for speed in speeds]) / len(speeds) # average time
        
        # Account for number of etch lines
        if perimeter > 2300:
            usage = usage + 0.5 
        elif thickness < 1:
            usage = usage + 0.2

    # Return multiplier adjusted usage
    return round(usage * 1.35, 2)

def edgegrind(short:float, long:float) -> float:
    '''Calculates the usage for the edgegrind cell.'''

    if type(short) == str:
        short = float(short)

    if type(long) == str:
        long = float(long)
    
    if long < 6:
        usage = 0.5
    elif (long * short) / 144 < 0.1:
        usage = 0.55
    elif (long * short) / 144 <= 1:
        usage = 0.63
    elif (long * short) / 144 < 3:
        usage = 1.25
    elif (long * short) / 144 < 5:
        usage = 1.41
    else:
        usage = 1.88
    
    return usage

def drill(size:str, num:int) -> float:
    '''Calculates the usage for the drill cell.'''

    if type(num) == str:
        num = int(num)
    
    # Check if size is valid
    if size not in config['drill'].keys():
        raise UsageError(f'Unable to calculate usage for size {size}')
    
    # Calculate usage
    usage = config['drill'][size] * num

    return usage

def saw(steel:bool, dist:float) -> float:
    '''Calculates the usage for the saw cell.'''

    if type(dist) == str:    
        dist = float(dist)
    
    # Check if length is valid and calculate usage
    if steel and dist in range(1, 21):
        usage = dist + 1
        
    elif (not steel) and dist in config['saw'].keys():
        usage = config['saw'][dist]
        
    else:
        raise UsageError(f'Unable to calculate usage for {'steel' if steel else 'non-steel'} length {dist}')

    return usage

def bend(bends:int, weight:float) -> float:
    '''Calculates the usage for the bend cell.
    
    Args:
        bends (int): Number of bends
        weight (float): Weight of part being bent
    
    Returns:
        float: Usage for bend cell
    '''

    if type(weight) == str:
        weight = float(bends)

    bends = str(int(bends))

    # Verify number of bends and calculate usage
    if weight < 50 and bends in config['bend']['small'].keys():
        usage = config['bend']['small'][bends]
    
    elif weight >= 50 and bends in config['bend']['large'].keys():
        usage = config['bend']['large'][bends]
    
    else:
        raise UsageError(f'Unable to calculate usage for {bends} bends with weight {weight}')

    return usage

def weld(size:float, weight:float, num_parts:int, inches:float, fixturing:bool) -> float:
    '''Calculates the usage for the weld cell.
    
    Args:
        size (float): Size of weld (in inches)
        weight (float): Weight of part being welded
        num_parts (int): Number of parts to weld
        inches (float): Total length to weld (in inches)
        fixturing (bool): Part has fixturing
    
    Returns:
        float: Usage for weld cell
    
    Notes:
        The formula for the weld cell is:
        ( ( (hoist_factor + prep_factor + weld_time) * 2) + fitup_factor ) / 2) * breaks_factor
        
        Where:
            hoist_factor is 10 for weights over 300, 5 for weights between 51 and 300, and 0 for weights less than 50
            prep_factor is the part prep factor times the number of parts
            weld_time is the total length of weld divided by the weld speed
            fitup_factor is calculated as follows:
                if weight < 50, fitup_factor is 0
                if weight > 300, fitup_factor is prep_factor
                otherwise, fitup_factor is prep_factor * 0.05 plus the part fitup factor times the number of parts
            breaks_factor is the factor for breaks in the weld cell
    
    '''

    # Get weld speed
    for setting in config['weld']['size']:
        if setting[0] == size:
            speed = setting[1]

    # Hoist/Safety Factor 
    if weight > 300:
        hoist_factor = 10
    elif weight > 50:
        hoist_factor = 5
    else:
        hoist_factor = 0


    # Part prep factor
    prep_factor = config['weld']['part_prep'] * num_parts


    # Weld time
    weld_time = inches / speed


    # Fit-up factor
    if weight < 50:
        fitup_factor = 0
    elif weight > 300:
        fitup_factor = prep_factor
    else:
        fitup_factor = prep_factor * 0.05

    if num_parts < 10:
        fitup_factor += prep_factor * config['weld']['part_fitup'][0]
    elif num_parts > 20:
        fitup_factor += prep_factor * config['weld']['part_fitup'][2]
    else:
        fitup_factor += prep_factor * config['weld']['part_fitup'][1]
    
    if fixturing:
        fitup_factor += 0
    else:
        fitup_factor += prep_factor * 0.2


    # Calculate usage
    usage = ((((hoist_factor + prep_factor + weld_time) * 2) + fitup_factor)/2) * config['weld']['breaks_factor']

    return round(usage, 3)

def paint(length:float) -> float:
    '''Calculates the usage for the paint cell.'''

    if type(length) == str:
        length = float(length)

    if length < 24:
        usage = length / 2
    else:
        usage = ((24 / length) + 2) * 12
    
    return usage

class UsageError(Exception):
    """Exception raised for invalid usage"""

    def __init__(self, message):
        super().__init__(message)
