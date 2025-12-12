import sys
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.console import Console

from epubeditor.cli import inputHandler

console = Console()

session = PromptSession()
books = inputHandler()

# Стилизация
style = Style.from_dict({
    'prompt': 'green bold',
    'completion-menu': 'bg:#202020 fg:white',
    'scrollbar.background': 'bg:#101010'
})


def main(commandHandler, compl, help_message: str, path: str = 'epubeditor', args = []):
    if isinstance(compl, list):
        compl.append('help')
        compl.append('exit')
        completer = WordCompleter(compl)
    else:
        completer = compl
    
    # Обработка длины названия книги, чтоб оно было справа
    columns, lines = os.get_terminal_size()
    path_len = len(path) + 2
    max_name_len = columns - 10 - path_len
    
    if len(books) > 1:
        book_name = f'Books: {len(books)}'
    elif len(books) == 1:
        book_name = books[0].stem
    else:
        book_name = ''
    
    if len(book_name) > max_name_len:
        name_beginning = book_name[:5]
        name_end = book_name[-(max_name_len - 8):]
        book_name = name_beginning + '...' + name_end
    
    indent = columns - path_len - len(book_name)
    gap = ' ' * indent
    cursor = '>>> '
    
    first_append_in_args = True
    try:
        while True:
            console.print(f'[dim][[/][bold cyan]{path}[/][dim]][/]', gap, f'[bold blue]{book_name}[/]', sep = '')
            command = session.prompt(
                cursor,
                completer=completer,
                style=style
            ).strip()
            
            # Очистка двух строк
            print('\033[F\033[K', end='')
            print('\033[F\033[K', end='')
            console.print(f'[bold #008701]{cursor}[/]{command}')
            
            if not first_append_in_args:
                args.pop()
                first_append_in_args = True
            
            # Обработка дополнительных значений в коммандае
            if ' ' in command:
                index = command.find(' ')
                
                args.append(command[index + 1:])
                last_arg = args[-1]
                l_words = last_arg.split()
                new_last_arg = ''
                for word in l_words:
                    if word[:2] == '~/':
                        word = os.path.expanduser(word)
                    
                    if word != l_words[-1]:
                        new_last_arg += word + ' '
                    else:
                        new_last_arg += word
                
                if new_last_arg:
                    args[-1] = new_last_arg
                
                first_append_in_args = False
                
                command = command[:index]
            
            exit_or_back = 'exit'
            if path != 'epubeditor':
                exit_or_back = '..'
            
            command = command.lower()
            if command == 'help':
                console.print(help_message)
            elif path != 'epubeditor' and command == 'exit':
                return command
            elif command == exit_or_back:
                break
            elif args:
                if commandHandler(command, args) == 'exit':
                    return 'exit'
            else:
                if commandHandler(command) == 'exit':
                    return 'exit'
            
                
    except (KeyboardInterrupt, EOFError):
        sys.exit()

if __name__ == '__main__':
    print("This is just module, try to run cli.py")
