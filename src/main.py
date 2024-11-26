import warnings, rich
warnings.filterwarnings("ignore", category=SyntaxWarning)

import commands, typing, yaml, os

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
    
    command, options, args = parse_args(x)

    # Check for help command
    if command == 'help':
        commands.help(options, args)
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


    # Check options
    for option in options:
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
    func(options, args)
    
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

    args = input

    return command, flags, args


if __name__ == '__main__':

    os.system('cls' if os.name == 'nt' else 'clear') # Clear screen
    rich.print(messages['intro']) # Intro message
    
    # Main loop
    while True:
        try:
            main()
        except KeyboardInterrupt:
            commands.exit()
        except Exception as e:
            print(e)
            rich.print('[bold red]UNABLE TO RUN PREVIOUS COMMAND.[/bold red]\n\n')
