import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

import os, sys, yaml, scripts, calculate, pynput, re, route, time
import rich, rich.table
# Read available commands from config file
with open(r'config/command_config.yml', 'r') as f:
    command_data = yaml.load(f, Loader=yaml.Loader)

# Read configured messages
with open(r'config/messages.yml', 'r') as f:
    messages = yaml.load(f, Loader=yaml.Loader)

def help(options:list, args:list=None):
    '''Prints information about the program or a specific command.
    
    Args:
        options (list): List of command options. Not currently used.
        args (list): List of commands to print information about.
    '''

    def command_help(command:str):
        '''Prints help for a specific command'''

        rich.print(f'\t[bold]{command}[/bold]\n\t[cyan]\u2022[/cyan] {command_data[command]["description"]}')
        
        aliases = command_data[command]["aliases"]
        
        if len(aliases) > 0: 
            rich.print(f'\tAliases: [yellow]{command_data[command]["aliases"]}[/yellow]\n')
        else:
            rich.print('\t[light grey]No aliases.[/light grey]\n')
        
        for line in command_data[command]['help'].split('\n'): 
            rich.print(f'\t\t{line}')

    if len(args) > 0:
        for command in args:
            if command in command_data.keys():
                command_help(command)
            else:
                rich.print(f'[red]Command [/red][yellow]{command}[/yellow][red] not found[/red]')
    else:
        for command in command_data.keys():
            command_help(command)

    return

def part(option:str, args:list):

    # Check args
    if not (option in ['-l', '--locator']):
        
        if args == [] and option is not '-l':

            return
        
        elif not scripts.part_check_args(args):

            rich.print(f'[bold red]Invalid args provided: [white]{args}[/white].[/bold red]\n')

            return
    
    # Run command with the given option
    scripts.match_sequence(args, option, 'part')

def weldment(option:str, args:list):

    if option == False: return
    
    # Run command with the given option

    kb = pynput.keyboard.Controller()

    match option:

        case '--macro' | '-m': # Runs the oracle new routing macro

            rich.print(messages['weld']['macro_option'])
            
            # Construct record sequence
            records = scripts.construct_record_sequence(args, item='weld')
            
            # Execute macro
            pn = scripts.get_part_number()
            locator = scripts.get_locator()

            if records == None or pn == None or locator == None:
                return

            route.route_macro(kb, pn, records)
            route.locate_macro(kb, pn, locator)

        case _:
            
            # Construct record sequence
            records = scripts.construct_record_sequence(args, item='weld')

    pass

def tutorial(options:list, args:list):
    '''Runs a detailed, step-by-step, guided tutorial for this program'''

    try:
        scripts.run_tutorial()
    except KeyboardInterrupt:
        scripts.reset_screen()
    except Exception as e:
        scripts.clear_screen()
        rich.print(messages['tutorial']['error'])


def clear(options:list=None, args:list=None):

    scripts.clear_screen()
    return

def exit(options:list=None, args:list=None):
    
    print('\n\nExiting...')
    sys.exit()
    pass