import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

import commands, typing, yaml, os, rich
import scripts

# Read available commands from config file
with open('../config/command_config.yml', 'r') as f:
    available_commands = yaml.load(f, Loader=yaml.Loader)

# Read configured messages
with open('../config/messages.yml', 'r') as f:
    messages = yaml.load(f, Loader=yaml.Loader)

# Construct help command configuration
help_command = {
    'help': {
        'description' : 'Display information about the program or a specific command.',
        'aliases' : [],
        'options' : [],
        'args' : list(available_commands.keys()),
        'func' : 'help'
        }
    }

def main():

    x = input(' >> ')

    # Check for command
    if x.strip() == '':
        return
    
    user_input = parse_args(x)

    if user_input is None:
        return
    else:
        command, option, args = user_input



    # Check for help command
    if command == 'help':
        commands.help(option, args)
        return

    # Check command
    if command in available_commands.keys():
        command = available_commands[command]
    
    else:
        # Check aliases
        for key in available_commands.keys():
            if command in available_commands[key]['aliases']:
                command = available_commands[key]
                break
        
        if type(command) == str:
            rich.print(f'[bold red]Invalid command provided: [white]{command}[/white].[/bold red]\n')
            return


    # Check option
    if option not in command['options']:
        rich.print(f'[bold red]Invalid option provided: [white]{option}[/white]. Available options: [yellow]{command["options"]}[/yellow].[/bold red]\n')
        return    
    
    # Check args
    for arg in args:
        if arg not in command['args']:
            rich.print(f'[bold red]Invalid argument provided: [white]{arg}[/white]. Available arguments: [yellow]{command["args"]}[/yellow].[/bold red]\n')
            return
        
    # Run command
    func = getattr(commands, command['func'])
    func(option, args)
    
    return 

def parse_args(input:str) -> typing.Tuple[str, list[str], list[str]]:

    if input.strip() == None:
        return None

    # Split input into flags and arguments
    input = input.split(' ')
    input = [_ for _ in input if _ != '']

    command = input.pop(0)
    flags = []
    for _ in input[:]:
        if _[0] == '-':
            flags.append(_)
            input.remove(_)

    if len(flags) > 1:
        rich.print('[bold red] More than one option provided. Not currently supported.[/bold red]')
        return
    
    args = input

    return command, flags[0], args


if __name__ == '__main__':

    os.system('cls' if os.name == 'nt' else 'clear') # Clear screen
    scripts.print_intro()
    
    # Main loop
    while True:
        try:
            main()
        except KeyboardInterrupt:
            commands.exit()
        except Exception as e:
            print(e.with_traceback())
            rich.print('[bold red]UNABLE TO RUN PREVIOUS COMMAND.[/bold red]\n\n')
