import sys
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

session = PromptSession()

# Стилизация
style = Style.from_dict({
    'prompt': 'green bold',
    'completion-menu': 'bg:#202020 fg:white'
})


def main(commandHandler, compl: list, help_message: str, path: str = 'epubeditor', args = []):
    compl.append('help')
    compl.append('exit')
    completer = WordCompleter(compl)
    
    first_append_in_args = True
    try:
        while True:
            command = session.prompt(
                f'[{path}]\n' + '>>> ',
                completer=completer,
                style=style
            )
            
            if ' ' in command:
                index = command.find(' ')
                if first_append_in_args:
                    args.append(command[index + 1:])
                    if args[-1][:2] == '~/':
                        args[-1] =  os.path.expanduser(args[-1])
                    first_append_in_args = False
                else:
                    args[-1] = command[index + 1:]
                    if args[-1][:2] == '~/':
                        args[-1] =  os.path.expanduser(args[-1])
                command = command[:index]
            
            command = command.lower()
            if command == 'help':
                print(help_message)
            elif command == 'exit':
                break
            elif args:
                commandHandler(command, args)
            else:
                commandHandler(command)    
            
                
    except (KeyboardInterrupt, EOFError):
        sys.exit()

if __name__ == '__main__':
    print("This is just module, try to run cli.py")