from rich.console import Console
from prompt_toolkit import prompt

from epubeditor.console_prompt import style


console = Console()

def input(question, default = '', completer = None):
    console.print(f'[blue]{question}[/]')
    answer = prompt('> ', default = default, style = style, completer = completer)
    
    print('\033[F\033[K', end='')
    print('\033[F\033[K', end='')
    
    return answer