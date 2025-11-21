from rich import print
from prompt_toolkit import prompt

from src.console_prompt import style

def input(question, default = ''):
    print(f'[blue]{question}[/]')
    answer = prompt('> ', default = default, style = style)
    return answer