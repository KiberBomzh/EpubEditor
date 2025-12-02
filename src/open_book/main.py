import tempfile
import zipfile
import subprocess
from pathlib import Path
from prompt_toolkit.completion import PathCompleter

from src.open_book import search
from src.open_book.files_operations import main as do_with_file
from src.open_book.multiple_renamer import main as multiple_renamer
from src.open_book.completer import OpenCompleter
from src.open_book.functions import ls, tree
from src.metadata_editor import main as metadata_editor
from src.toc.main import main as tocEditor

from src.console_prompt import main as prompt

subprocess_errors = []

def toPretty(temp_path, args):
    book = args[0]
    file_formats = ['.xhtml', '.html', '.htm', '.xml', '.opf', '.ncx']
    for file in temp_path.rglob('*'):
        if file.is_file() and file.suffix.lower() in file_formats:
            result = subprocess.run(["xmllint", file, "--format", "-o", file], capture_output = True, text = True)
            
            if result.stderr:
                subprocess_errors.append(f"--------------------\n{book}\n{file.relative_to(temp_path)}\n{result.stderr}")
            
            print(file.relative_to(temp_path))

# Переменная с ошибками открытия zip
zip_errors = []

def openBook(book_path, func, args = []):
    #Извлечение всех файлов книги во временную папк
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        compression_info = {}
        with zipfile.ZipFile(book_path, 'r') as book_read:
            for item in book_read.infolist():
                compression_info[item.filename] = item.compress_type
            try:
                book_read.extractall(temp_path)
            except zipfile.BadZipFile:
                zip_errors.append(book_path)
                return None
        
        if args:
            func(temp_path, args)
        else:
            func(temp_path)
        
        #Запись книги из временной папки (сохранение изменений)
        temp_book = book_path.with_suffix('.temp.zip')
        try:
            with zipfile.ZipFile(temp_book, 'w') as book_write:
                for file in temp_path.rglob('*'):
                    if file.is_file():
                        arcname = file.relative_to(temp_path).as_posix()
                        compress_type = compression_info.get(
                            arcname, 
                            zipfile.ZIP_DEFLATED
                        )
                        book_write.write(
                            file, 
                            arcname, 
                            compress_type=compress_type
                        )
            temp_book.replace(book_path)
        finally:
            if temp_book.exists():
                temp_book.unlink()

def save(temp_path, book):
    # Запись книги из временной папки (сохранение изменений)
    temp_book = book.with_suffix('.temp.zip')
    try:
        with zipfile.ZipFile(temp_book, 'w') as book_write:
            for file in temp_path.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(temp_path).as_posix()
                    book_write.write(file, arcname)
        temp_book.replace(book)
    finally:
        if temp_book.exists():
            temp_book.unlink()

def save_as(temp_path, book):
    # Запись книги из временной папки (сохранение изменений)
    with zipfile.ZipFile(book, 'w') as book_write:
        for file in temp_path.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(temp_path).as_posix()
                book_write.write(file, arcname)

def optionHandl(action, args):
    book = args[0]
    temp_path = args[1]
    
    if len(args) > 2:
        arg = args[2].strip()
        file = temp_path / arg
    else:
        arg = ''
    
    match action:
        case 'save':
            save(temp_path, book)
        case 'save_as':
            if arg:
                book_as = Path(arg)
                if book_as.parent.exists():
                    save_as(temp_path, book_as)
                else:
                    print(f'Invalid path: {book_as}, try again:')
            
            else:
                print("Option needs second argument.")
        
        case 'meta':
            from src.editor.main import getOpf
            
            container = temp_path / 'META-INF/container.xml'
            opf = temp_path / getOpf(container)
            return metadata_editor.main(opf, path = 'epubeditor/open/meta')

        case 'toc':
            from src.editor.main import getOpf, getToc
            
            container = temp_path / 'META-INF/container.xml'
            opf = temp_path / getOpf(container)
            toc, what_is_it = getToc(opf)
            toc = opf.parent / toc
            
            return tocEditor(toc, opf, what_is_it, path = 'epubeditor/open/toc')

        case 'search':
            if arg:
                replace_spliter = ' &replace_to '
                if replace_spliter in arg:
                    query, new_value = arg.split(replace_spliter)
                    search.main(temp_path, query, 'replace', new_value)
                else:
                    search.main(temp_path, arg, 'print')
            else:
                print("Option needs second argument.")
        
        case 'micro' | 'nano' | 'vim' | 'nvim' | 'bat':
            if arg:
                subprocess.run([action, file])
            else:
                print("Option needs second argument.")
        
        case 'pretty':
            file_formats = ['.xhtml', '.html', '.htm', '.xml', '.opf', '.ncx']
            for file in temp_path.rglob('*'):
                if file.is_file() and file.suffix.lower() in file_formats:
                    subprocess.run(["xmllint", file, "--format", "-o", file])
            
                    print(file.relative_to(temp_path))
        
        case 'tree':
            tree(temp_path, book.stem)
        case 'ls':
            ls(temp_path)
        case 'just_ls':
            for f in temp_path.rglob('*'):
                print(f.relative_to(temp_path))
        case 'rm' | 'add' | 'rename':
            if arg:
                do_with_file(temp_path, action, arg)
            else:
                if action == 'rename':
                    multiple_renamer(temp_path)
                else:
                    print("Option needs second argument.")
        case _:
            print("Unknown option, try again.")

def main(book):
    helpmsg = ("Options:\n" +
        "\t-Save                        [green]'save'[/]\n" +
        "\t-Save as                     [green]'save_as'[/] [cyan]'path/to/book_as.epub'[/]\n" +
        "\t-Metadata editor             [green]'meta'[/]\n" +
        "\t-Table of contents editor    [green]'toc'[/]\n" +
        "\t-Search in files             [green]'search'[/] [magenta]'query'[/]\n" +
        "\t-Search and replace          [green]'search'[/] [magenta]'query'[/] [dark_orange]&replace_to[/] [magenta]'new value'[/]\n" +
        "\t-Open in text editor         [green]'{micro/nano/vim/nvim/bat}'[/] [cyan]full/file/name.suffix[/]\n" +
        "\t-Format .xml files           [green]'pretty'[/]\n" +
        "\t-Print book's tree           [green]'tree'[/]\n" +
        "\t-Print all files             [green]'ls'[/]\n" +
        "\t-ls without formatting       [green]'just_ls'[/]\n" +
        "\t-Delete files                [green]'rm'[/]\n" +
        "\t-Add file                    [green]'add'[/]\n" +
        "\t-Rename                      [green]'rename'[/]\n" +
        "\t-Go back                     [green]'..'[/]\n" +
        "\t-Exit")
    
    #Извлечение всех файлов книги во временную папк
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(book, 'r') as book_read:
            try:
                book_read.extractall(temp_path)
                
                global_completer = PathCompleter(
                    expanduser=True,  # Раскрывать ~ в домашнюю директорию
                    file_filter=lambda name: '.' != Path(name).stem[0],
                    min_input_len=0,  # Показывать сразу
                    get_paths=lambda: ['.'],
                )
                book_completer = PathCompleter(
                    min_input_len=0,
                    get_paths=lambda: [temp_path]
                )
                book_dest_completer = PathCompleter(
                    file_filter=lambda name: Path(name).is_dir(),
                    min_input_len=0,
                    get_paths=lambda: [temp_path]
                )
                
                completer = OpenCompleter({
                    'save': None,
                    'save_as': global_completer, # Один путь
                    'meta': None,
                    'toc': None,
                    'search': None,
                    'micro': book_completer, # Тут везде один путь
                    'nano': book_completer,
                    'vim': book_completer,
                    'nvim': book_completer,
                    'bat': book_completer,
                    'pretty': None,
                    'tree': None,
                    'ls': None,
                    'just_ls': None,
                    'rm': book_completer, # Много
                    # Сложное дополнение сначала много, потом - один
                    'add': {global_completer: {'to': book_dest_completer}},
                    'rename': book_completer, # Много
                    '..': None,
                    'exit': None,
                    'help': None,
                }, global_completer, book_completer, book_dest_completer, ['rename', 'rm'])
                
                return prompt(optionHandl, completer, helpmsg, path = 'epubeditor/open', args = [book, temp_path])
            except zipfile.BadZipFile:
                print(book)
                print("Bad zip file! Possible zipbomb!")
                return None
        

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
