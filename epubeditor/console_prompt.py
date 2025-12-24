import sys
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.console import Console

console = Console()

session = PromptSession()

# Стилизация
style = Style.from_dict({
    'prompt': 'green bold',
    'completion-menu': 'bg:#202020 fg:white',
    'scrollbar.background': 'bg:#101010'
})


def get_name(books, path):
    # Обработка длины названия книги, чтоб оно было справа
    columns, lines = os.get_terminal_size()
    path_len = len(path) + 2
    max_name_len = columns - 10 - path_len
    
    book_name = ''
    if isinstance(books, list):
        if len(books) > 1:
            book_name = f'Books: {len(books)}'
        elif len(books) == 1:
            book_name = books[0].stem
    elif isinstance(books, str):
        book_name = books
    
    if len(book_name) > max_name_len:
        name_beginning = book_name[:5]
        name_end = book_name[-(max_name_len - 8):]
        book_name = name_beginning + '...' + name_end
    
    indent = columns - path_len - len(book_name)
    gap = ' ' * indent
    
    return gap, book_name

def main(commandHandler, compl, help_message: str, path: str = 'epubeditor', args = [], books = []):
    if isinstance(compl, list):
        compl.append('help')
        compl.append('exit')
        completer = WordCompleter(compl)
    else:
        completer = compl
    
    if not books:
        from epubeditor import books
    
    cursor = '>>> '
    first_append_in_args = True
    try:
        while True:
            gap, book_name = get_name(books, path)
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
            
            try:
                command = command.lower()
                if command == 'help':
                    console.print(help_message)
                elif path != 'epubeditor' and command == 'exit':
                    return command
                elif command == exit_or_back:
                    break
                elif args:
                    resp = commandHandler(command, args)
                    if resp == 'exit':
                        return resp
                    elif isinstance(resp, list):
                        books = resp
                else:
                    resp = commandHandler(command)
                    if resp == 'exit':
                        return resp
                    elif isinstance(resp, list):
                        books = resp
            except Exception as err:
                console.print("[red]Error:[/]")
                print(err)
                
    except (KeyboardInterrupt, EOFError):
        sys.exit()

if __name__ == '__main__':
    print("This is just module, try to run cli.py")
