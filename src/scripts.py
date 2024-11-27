from pynput import keyboard, mouse
from time import sleep
import re, calculate, os, rich, yaml

import rich.table
from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import Key
from watcher import Watcher

# Read configured messages
with open('../config/messages.yml', 'r') as f:
    messages = yaml.load(f, Loader=yaml.Loader)

# Read available commands from config file
with open('../config/command_config.yml', 'r') as f:
    command_data = yaml.load(f, Loader=yaml.Loader)

def get_part_number() -> str:

    while True:
        try:
            pn = input(f"\tEnter part number: ")

            pattern = r'^\d{9}$'

            if re.match(pattern, pn):
                return pn
            else:
                rich.print('[bold red]Invalid part number.[/bold red]\n')

        except KeyboardInterrupt:
            print('\n')
            return
            
def get_locator() -> str:
    
    while True:
        try:
            locator = input(f"\tEnter locator: ")

            # Must follow the pattern dd-dd or dd-CUSTOM
            pattern = r'^\d{2}-\d{2}$|^\d{2}-CUSTOM$|^32-[A-Z]$|^NEW ITEM 1$'

            if re.match(pattern, locator):
                return locator
                
            else:
                rich.print('[bold red]Invalid locator.\n[bold red]')

        except KeyboardInterrupt:
            print('\n')
            return

def get_usage(message:str, pattern:str) -> str:
    
    while True:
        try:
            val = input('\t' + message)
        except KeyboardInterrupt:
            print('\n')
            return
        
        if val == '':
            rich.print('[bold red]Empty values not allowed.[/bold red]\n')

        if re.match(pattern, val):
            return val
        else:
            rich.print('[bold red]Invalid input.[/bold red]\n')

def part_check_args(args:list) -> bool:
    '''Check args for the part command. Returns True if valid, False if not'''

    # Check args

    # Check for no args
    if len(args) == 0:
        rich.print('[bold red]No cells provided.[/bold red]\n')
        return False
    
    # Check for invalid args
    for arg in args:
        if arg not in command_data['part']['args']:
            rich.print(f'[bold red]Invalid cell provided: [white]"{arg}"[/white]. Available cells: [yellow]{command_data['part']['args']}[/yellow].[/bold red]\n')
            return False
    
    # Check for duplicate args
    if len(args) != len(set(args)):
        rich.print('[bold red]Duplicate cells provided.[/bold red]\n')
        return False

    return True

def part_check_options(options:list) -> bool:
    '''Check options for the part command. Returns True if valid, False if not'''

    if len(options) > 1:
        rich.print('[bold red]Too many options provided. [/bold red]\n')
        return False
    
    if len(options) == 1:
        option = options[0]

        if option not in command_data['part']['options']:
            rich.print(f'[bold red]Invalid option provided: "[white]{option}[/white]". Available options: {command_data["part"]["options"]}[/bold red]\n')
            return False

    return True

def construct_record_sequence(args:list) -> list:

    # Check args
    if args == []:
        return
    elif not part_check_args(args):
        rich.print(f'[bold red]Invalid args provided: [white]{args}[/white].[/bold red]\n')
        return

    records = []

    for index, cell in enumerate(args):
        
        # Get all neccessary data from the user
        cell_data = command_data['part']['data'][cell]
        kwargs = {}

        for param, data in cell_data['params'].items():
            
            message = data[0]
            pattern = data[1]
            
            usage = get_usage(message, pattern)
            
            if usage is None:
                return
            
            kwargs[param] = usage
            
        
        # Get usage
        func = getattr(calculate, cell_data['calc_func'])
        try:
            usage = func(**kwargs)
        except calculate.UsageError as e:
            rich.print(e)
            rich.print("[bold red]Please try again...[/bold red]\n")
            return

        # Construct record
        record = [str((index + 1) * 10)] + cell_data['record']
        record.insert(3, usage)

        records.append(record)

    # Print table
    print_table(records)

    return records

def print_table(records:list) -> None:

    # Print records in a nicely formatted rich table
    table = rich.table.Table()

    # Add columns to the table
    table.add_column("Seq", style="white", no_wrap=True)
    table.add_column("Cell Name", style="cyan")
    table.add_column("Machinist", style="white")
    table.add_column("Usage", style="cyan")
    table.add_column("Description", style="white")

    # Add records to the table
    for record in records:
        table.add_row(*[str(_) for _ in record])

    print('\n\n')
    rich.print(table)
    print('\n')
    return

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def reset_screen():
    clear_screen()
    print_intro()

def run_tutorial():
    clear_screen()
    rich.print(messages['tutorial']['welcome'])

    if not input() == 'y':
        reset_screen()
        return
    
    clear_screen()
    rich.print(messages['tutorial']['step_1'])

    if not input() == 'y':
        rich.print('[bold red]Check with your supervisor or open a different part number.[/bold red]\n')
        input('Press enter to exit the tutorial...')
        reset_screen()
        return
    
    clear_screen()
    rich.print(messages['tutorial']['step_2'])

    while input(' >> ') != 'part l e b P':
        rich.print('Not quite! Enter "[yellow]part l e b P[/yellow]" exactly.')

    clear_screen()
    rich.print(messages['tutorial']['step_3'])
    records = construct_record_sequence(['l', 'e', 'b', 'P'])

    clear_screen()
    rich.print('Congrats! You generated a set of records that make up a routing.\n')
    rich.print(messages['tutorial']['step_4'])
    table = rich.table.Table()

    # Add columns to the table
    table.add_column("Seq", style="white", no_wrap=True)
    table.add_column("Cell Name", style="white")
    table.add_column("Machinist", style="white")
    table.add_column("Usage", style="white")
    table.add_column("Description", style="white")

    correct_records = [['10', '250001', 'MACHINIST', 0.42, 'LASER CUT PART'],
               ['20', 'EDGEGRIND', 'MACH OPER', 0.63, 'GRIND EDGES'],
               ['30', '101001', 'MACHINIST', 1.5, 'FORM BENDS'],
               ['40', '095424', 'PAINTER', 1.75, 'POWDER PAINT PART']]
    # Add records to the table
    count_incorrect = 0
    for i, record in enumerate(records):

        if correct_records[i][3] != record[3]:
            table.add_row(*[str(_) for _ in record], style='red')
            count_incorrect += 1
        else:
            table.add_row(*[str(_) for _ in record], style='green')
    
    rich.print(table)
    if count_incorrect == 0:
        rich.print('[green]All records are correct![/green]')
    else:
        rich.print(f'You created [bold red]{count_incorrect}[/bold red] incorrect records.')

    rich.print(messages['tutorial']['step_5'])

    input('Press enter to exit the tutorial...')
    reset_screen()

def print_intro():
    rich.print(messages['intro'])

    for command in command_data.keys():
        rich.print(f' [bold cyan]\u2022[/bold cyan] [yellow]{command}[/yellow] - {command_data[command]["description"]}')
