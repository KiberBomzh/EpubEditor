from rich import print
from prompt_toolkit import prompt

from epubeditor.console_prompt import style

def input(question, default = '', completer = None):
    print(f'[blue]{question}[/]')
    answer = prompt('> ', default = default, style = style, completer = completer)
    return answer