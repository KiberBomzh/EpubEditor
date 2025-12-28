import tempfile
import zipfile
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from prompt_toolkit.completion import PathCompleter

from epubeditor.open_book import search
from epubeditor.open_book.files_operations import main as do_with_file
from epubeditor.open_book.multiple_renamer import main as multiple_renamer
from epubeditor.open_book.completer import OpenCompleter
from epubeditor.open_book.functions import ls, tree
from epubeditor.metadata_editor import main as metadata_editor
from epubeditor.toc.main import main as tocEditor
from epubeditor.open_book.split import main as split
from epubeditor.open_book.merge import main as merge
from epubeditor.open_book.scripts import main as scripts
from epubeditor.open_book.scripts import scripts_list

from epubeditor.console_prompt import main as prompt
from epubeditor.config import autosave


subprocess_errors = []

def start_xmllint(file):
    result = subprocess.run(["xmllint", file, "--format", "-o", file], capture_output = True, text = True)
    return result

def toPretty(temp_path, args):
    book = args[0]
    file_formats = ['.xhtml', '.html', '.htm', '.xml', '.opf', '.ncx']
    with ThreadPoolExecutor(max_workers = 10) as executor:
        works = []
        for file in temp_path.rglob('*'):
            if file.is_file() and file.suffix.lower() in file_formats:
                works.append(executor.submit(start_xmllint, file))
        for work in works:
            result = work.result()
            if result.stderr:
                subprocess_errors.append(f"--------------------\n{book}\n{file.relative_to(temp_path)}\n{result.stderr}")
    # print(f"{book.parent.name}/{book.name}")


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

def extract(in_file):
    if not in_file.is_file():
        print(f'Invalid path: {in_file}, try again:')
        return

    out_path = Path.cwd()
    subprocess.run(['cp', in_file, out_path])

def save_as(temp_path, out_path, book):
    if out_path.is_dir():
        book_as = get_free_name_as(out_path, book)
    elif out_path.parent.exists():
        book_as = out_path
    else:
        print(f'Invalid path: {out_path}, try again:')
        return

    with zipfile.ZipFile(book_as, 'w') as book_write:
        for file in temp_path.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(temp_path).as_posix()
                book_write.write(file, arcname)

def get_free_name_as(path, book):
    book_as = path / (book.stem + '_as' + book.suffix)
    counter = 0
    while book_as.exists():
       counter += 1
       book_as = path / (book.stem + '_as' + f'({counter})' + book.sufiix)
    return book_as

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
                out_path = Path(arg)
                save_as(temp_path, out_path, book)
            else:
                out_path = Path.cwd()
                book_as = get_free_name_as(out_path, book)
                save_as(temp_path, book_as, book)
        
        case 'extract':
            if arg:
                extract(file)
            else:
                print("Option needs second argument.")
        
        case 'merge':
            if arg:
                merge(temp_path, arg)
            else:
                print("Option needs second argument.")
        
        case 'split':
            if arg:
                split(temp_path, arg)
            else:
                print("Option needs second argument.")

        case 'meta':
            from epubeditor.editor.main import getOpf
            
            container = temp_path / 'META-INF/container.xml'
            opf = temp_path / getOpf(container)
            return metadata_editor.main(opf, books = [book], path = 'epubeditor/open/meta')

        case 'toc':
            from epubeditor.editor.main import getOpf, getToc
            
            container = temp_path / 'META-INF/container.xml'
            opf = temp_path / getOpf(container)
            toc_tuple_str, what_is_it = getToc(opf)
            toc = (opf.parent / toc_tuple_str[0]).resolve()
            
            if what_is_it == 'toc and nav':
                nav = (opf.parent / toc_tuple_str[1]).resolve()
                toc_tuple = (toc, nav)
            else:
                toc_tuple = (toc,)
            
            return tocEditor(toc_tuple, opf, what_is_it, books = [book], path = 'epubeditor/open/toc')

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
        
        case 'micro' | 'nano' | 'vim' | 'nvim' | 'bat' | 'chafa':
            if arg:
                subprocess.run([action, file])
            else:
                print("Option needs second argument.")
        
        case 'pretty':
            subprocess_errors.clear()
            toPretty(temp_path, [book, arg])
            
            if subprocess_errors:
                print('Subprocess Error:')
                for error in subprocess_errors:
                    print(error)
        
        case 'tree':
            if arg:
                if file.is_dir():
                    tree(file, file.name)
                else:
                    print(f"Not valid path: {arg}, try again.")
            else:
                tree(temp_path, book.stem)
        case 'ls':
            if arg:
                if file.is_dir():
                    ls(file, separators = False)
                else:
                    print(f"Not valid path: {arg}, try again.")
            else:
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
        case 'script':
            if arg:
                scripts(temp_path, arg)
            else:
                print("Option needs second argument.")
        case _:
            print("Unknown option, try again.")

def main(book):
    helpmsg = ("Options:\n" +
        "\t-Save                        [green]'save'[/]\n" +
        "\t-Save as                     [green]'save_as'[/] [cyan]'path/to/book_as.epub'[/]\n" +
        "\t-Extract file                [green]'extract'[/] [cyan]'path/to/file'[/]\n" +
        "\t-Merge files                 [green]'merge'[/] [cyan]'path/to/main_file'[/] [dark_orange]how many files merge (number)[/]\n" +
        "\t-Split files                 [green]'split'[/] [cyan]'path/to/file'[/] : [cyan]'path/to/file'[/]\n" +
        "\t-Metadata editor             [green]'meta'[/]\n" +
        "\t-Table of contents editor    [green]'toc'[/]\n" +
        "\t-Search in files             [green]'search'[/] [magenta]'query'[/]\n" +
        "\t-Search and replace          [green]'search'[/] [magenta]'query'[/] [dark_orange]&replace_to[/] [magenta]'new value'[/]\n" +
        "\t-Open in text editor         [green]'{micro/nano/vim/nvim/bat}'[/] [cyan]full/file/name.suffix[/]\n" +
        "\t-Open image                  [green]'chafa' [/] [cyan]path/to/image.jpg[/]\n" +
        "\t-Format .xml files           [green]'pretty'[/]\n" +
        "\t-Print book's tree           [green]'tree'[/] or you can use [green]'tree'[/] [cyan]'path/to/folder'[/]\n" +
        "\t-Print all files             [green]'ls'[/] or you can use [green]'ls'[/] [cyan]'path/to/folder'[/]\n" +
        "\t-ls without formatting       [green]'just_ls'[/]\n" +
        "\t-Delete files                [green]'rm'[/]\n" +
        "\t-Add file                    [green]'add'[/]\n" +
        "\t-Rename                      [green]'rename'[/]\n" +
        "\t-Start script                [green]'script' name[/]\n" +
        "\t-Go back                     [green]'..'[/]\n" +
        "\t-Exit")
    
    scripts_dict = {}
    for scr in scripts_list:
        scripts_dict[scr] = None
    
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
                global_dest_completer = PathCompleter(
                    expanduser=True,
                    file_filter=lambda name: Path(name).is_dir() and Path(name).stem[0] != '.',
                    min_input_len=0,
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
                    'save_as': global_dest_completer, # Один путь
                    'extract': book_completer,
                    'merge': book_completer,
                    'split': book_completer,
                    'meta': None,
                    'toc': None,
                    'search': None,
                    'micro': book_completer, # Тут везде один путь
                    'nano': book_completer,
                    'vim': book_completer,
                    'nvim': book_completer,
                    'bat': book_completer,
                    'chafa': book_completer,
                    'pretty': None,
                    'tree': book_dest_completer,
                    'ls': book_dest_completer,
                    'just_ls': None,
                    'rm': book_completer, # Много
                    # Сложное дополнение сначала много, потом - один
                    'add': {global_completer: {'to': book_dest_completer}},
                    'rename': book_completer, # Много
                    'script': scripts_dict,
                    '..': None,
                    'exit': None,
                    'help': None,
                }, global_completer, global_dest_completer, book_completer, book_dest_completer, ['rename', 'rm', 'split'])
                
                act = prompt(optionHandl, completer, helpmsg, path = 'epubeditor/open', args = [book, temp_path], books = [book])
                if autosave:
                    save(temp_path, book)
                return act
            except zipfile.BadZipFile:
                print(book)
                print("Bad zip file! Possible zipbomb!")
                return None
        

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
