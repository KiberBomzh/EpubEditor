import tempfile
import zipfile
import subprocess
from pathlib import Path
from rich.console import Console

from src.open_book import search
from src.metadata_editor import main as metadata_editor

from src.console_prompt import main as prompt

subprocess_errors = []

def toPretty(temp_path, args):
    book = args[0]
    file_formats = ['.xhtml', '.html', '.htm', '.xml', '.opf', '.ncx']
    for file in temp_path.rglob('*'):
        if file.is_file() and file.suffix.lower() in file_formats:
            result = subprocess.run(["xmllint", file, "--format", "-o", file], capture_output = True, text = True)
            
            if result.stderr:
                subprocess_errors.append(f"--------------------\n{book}\n{result.stderr}")
            
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

def ls(temp_path):
    book_content = []
    css = []
    images = []
    fonts = []
    other = []
    opf = ''
    ncx = ''
    for file in temp_path.rglob('*'):
        if file.is_file():
            f = file.relative_to(temp_path)
            match file.suffix.lower():
                case '.xhtml' | '.html' | '.htm':
                    book_content.append(f)
                case '.jpg' | '.jpeg' | '.png':
                    images.append(f)
                case '.ttf' | '.otf':
                    fonts.append(f)
                case '.css':
                    css.append(f)
                case '.opf':
                    opf = f
                case '.ncx':
                    ncx = f
                case _:
                    other.append(f)
    
    if opf:
        console.print(f'[yellow]{opf}')
    if ncx:
        console.print(f'[cyan]{ncx}')
    
    for f in sorted(book_content):
        console.print(f'[green]{f}')
    
    for f in css:
        console.print(f'[blue]{f}')
    
    for f in fonts:
        console.print(f'[dark_orange]{f}')
    
    for f in images:
        console.print(f'[magenta]{f}')
    
    if other:
        for f in other:
            console.print(f'[dim]{f}')

def optionHandl(action, args):
    book = args[0]
    temp_path = args[1]
    
    if len(args) > 2:
        arg = args[2]
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
            opf = list(temp_path.rglob('*.opf'))[0]
            return metadata_editor.main(opf, path = 'epubeditor/open/meta')
        
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
        
        case 'micro' | 'nano' | 'vim' | 'bat':
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
            subprocess.run(['tree', temp_path])
        case 'ls':
            ls(temp_path)
        case 'just_ls':
            for f in temp_path.rglob('*'):
                print(f.relative_to(temp_path))
        #case 'cp'
        #case 'mv'
        #case 'rm'
        case _:
            print("Unknown option, try again.")

console = Console()

def main(book):
    helpmsg = ("Options:\n" +
        "\t-Save\n" +
        "\t-Save as, 'save_as' <book_as path>\n" +
        "\t-Metadata editor\n" +
        "\t-Search in files, 'search' <query>\n" +
        "\t-Open in text editor, 'micro, nano, vim, bat' <file_name>\n" +
        "\t-Pretty\n" +
        "\t-tree\n" +
        "\t-ls\n" +
        "\t-just_ls\n" +
        #"\t-cp\n" +
        #"\t-mv\n" +
        #"\t-rm\n" +
        "\tGo back, '..'\n" +
        "\t-Exit")
    optList = ['save', 'save_as', 'meta', 'search', 'micro', 'nano', 'vim', 'bat', 'pretty', 'tree', 'ls', 'just_ls', '..'] #, 'cp', 'mv', 'rm']
    
    #Извлечение всех файлов книги во временную папк
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(book, 'r') as book_read:
            try:
                book_read.extractall(temp_path)
            except zipfile.BadZipFile:
                print(book)
                print("Bad zip file! Possible zipbomb!")
                return None
        
        return prompt(optionHandl, optList, helpmsg, path = 'epubeditor/open', args = [book, temp_path])

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
