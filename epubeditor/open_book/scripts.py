from rich.console import Console
from pathlib import Path
import os
import subprocess

from epubeditor.scripts.toc_from_titles import main as toc_from_titles
from epubeditor.scripts.split_by_titles import main as split_by_titles
from epubeditor.scripts.clean_doubled_xml_declarations import main as clean_doubled_xml_declarations

from epubeditor.scripts import __all__ as scripts_list
from epubeditor import config


if config:
    if 'scripts' in config:
        if 'path' in config['scripts']:
            script_path = config['scripts']['path']
            if '~/' in script_path:
                script_path = os.path.expanduser(script_path)
            
            for file in Path(script_path).glob('*'):
                if os.access(file, os.X_OK):
                    scripts_list.append(file.name)
            
        else:
            script_path = ''


def main(temp_path, arg):
    if isinstance(arg, list):
        args = arg
        action = args[0]
    else:
        args = arg.split()
        action = args[0]
        if action not in scripts_list:
            print("There's no such script:", action)
            return
    
    console = Console()
    
    match action:
        case 'toc_from_titles':
            with console.status(f'[green]{action}[/]'):
                toc_from_titles(temp_path)
        case 'split_by_titles':
            split_by_titles(temp_path, console)
        case 'clean_doubled_xml_declarations':
            with console.status(f'[green]{action}[/]'):
                clean_doubled_xml_declarations(temp_path)
        case _:
            with console.status(f'[green]{action}[/]'):
                subprocess.run(
                    f'{script_path}/{action} "{temp_path}"', 
                    shell = True, 
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL
                )
