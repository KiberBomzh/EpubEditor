import sys
from rich import print

from epubeditor.input_handler import inputHandler

try:
    books = inputHandler()
except Exception as err:
    print(f"[red]{err}[/]")
    sys.exit()