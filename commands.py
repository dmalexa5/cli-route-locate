import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

import os, sys, yaml, scripts, calculate, pynput, re, route, time
import rich, rich.table
# Read available commands from config file
with open('command_config.yml', 'r') as f:
    command_data = yaml.load(f, Loader=yaml.Loader)

# Read configured messages
with open('messages.yml', 'r') as f:
    messages = yaml.load(f, Loader=yaml.Loader)

def help(options:list, args:list):
    scripts.clear_screen()
    rich.print(messages['help']['header'])

    try:
        input('\nPress enter to exit...')
    except KeyboardInterrupt:
        pass

    scripts.reset_screen()
    return

def part(options:list, args:list):

    # Check options
    if not scripts.part_check_options(options, command_data): return 
    elif len(options) == 1:
        option = options[0]
    else:
        option = ''
    
    # Run command under the given option conditions
    kb = pynput.keyboard.Controller()

    match option:

        case '--macro' | '-M': # Runs the oracle new routing macro
            rich.print(messages['part']['macro_option'])
            
            # Construct record sequence
            records = scripts.construct_record_sequence(args, command_data)
            
            # Execute macro
            pn = scripts.get_part_number()
            locator = scripts.get_locator()

            if records == None or pn == None or locator == None:
                return

            route.route_macro(kb, pn, records)
            route.locate_macro(kb, pn, locator)

        case '--update' | '-U': # Runs the oracle update routing macro
            rich.print(messages['part']['update_option'])

            rich.print(messages['part']['errpror']['not_implemented'])
        
        case '--locator' | '-L': # Runc the oracle locator macro ONLY
            rich.print(messages['part']['locator_option'])

            pn = scripts.get_part_number()
            locator = scripts.get_locator()

            if pn == None or locator == None:
                return
            
            route.locate_macro(kb, pn, locator)
        case _:
            
            # Construct record sequence
            records = scripts.construct_record_sequence(args, command_data)

def weldment(options:list, args:list):
    print(f'weldment function run with option: {options} and args: {args}')
    pass

def tutorial(options:list, args:list):
    '''Runs a detailed, step-by-step, guided tutorial for this program'''
    try:
        scripts.run_tutorial(command_data=command_data)
    except KeyboardInterrupt:
        scripts.reset_screen()
    except Exception as e:
        scripts.clear_screen()
        rich.print(messages['tutorial']['error'])
    pass

def clear(options:list=None, args:list=None):
    scripts.clear_screen()
    return

def exit(options:list=None, args:list=None):
    print('\n\nExiting...')
    sys.exit()
    pass