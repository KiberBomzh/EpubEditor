import tempfile
import zipfile
import subprocess
from pathlib import Path
from lxml import etree, html

from src.open_book import search
from src.metadata_editor import main as metadata_editor

from src.console_prompt import main as prompt

def toPretty(temp_path):
    file_formats = ['.xhtml', '.html', '.htm', '.opf', '.ncx']
    xml_form = file_formats[3:]
    html_form = file_formats[:3]
    for file in temp_path.rglob('*'):
        if file.is_file() and file.suffix.lower() in file_formats:
            #subprocess.run(["xmllint", file, "--format", "-o", file])
            if file.suffix.lower() in xml_form:
                tree = etree.parse(file)
                root = tree.getroot()
                pretty_content = (
                    '<?xml version="1.0" encoding="UTF-8"?>\n' + 
                    etree.tostring(root, pretty_print = True, encoding = 'unicode')
                )
                file.write_text(pretty_content, encoding = 'utf-8')
            elif file.suffix.lower() in html_form:
                tree = html.parse(file)
                root = tree.getroot()
                pretty_content = (
                    '<?xml version="1.0" encoding="UTF-8"?>\n' + 
                    html.tostring(root, pretty_print = True, encoding = 'unicode')
                )
                file.write_text(pretty_content, encoding = 'utf-8')
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
    #Запись книги из временной папки (сохранение изменений)
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

def optionHandl(action, args):
    book = args[0]
    temp_path = args[1]
    fList = args[2]
    
    if len(args) > 3:
        arg = args[3]
        file = temp_path / arg
    else:
        arg = False
    
    match action:
        case 'save':
            save(temp_path, book)
        
        case 'meta':
            opf = list(temp_path.rglob('*.opf'))[0]
            metadata_editor.main(opf, path = 'epubeditor/open/meta')
        
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

        case 'tree':
            subprocess.run(['tree', temp_path])
        case 'ls':
            for f in fList:
                print(f)
        #case 'cp'
        #case 'mv'
        #case 'rm'
        case _:
            print("Unknown option, try again.")

def main(book):
    helpmsg = ("Options:\n" +
        "\t-Save\n" +
        "\tMetadata editor\n" +
        "\t-Search in files, 'search' <query>\n" +
        "\t-Open in text editor, 'micro, nano, vim, bat' <file_name>\n" +
        "\t-tree\n" +
        "\t-ls\n" +
        #"\t-cp\n" +
        #"\t-mv\n" +
        #"\t-rm\n" +
        "\t-Exit")
    optList = ['save', 'meta', 'search', 'micro', 'nano', 'vim', 'bat', 'tree', 'ls'] #, 'cp', 'mv', 'rm']
    
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
        
        fList = []
        for f in temp_path.rglob('*'):
            fList.append(f.relative_to(temp_path))
        prompt(optionHandl, optList, helpmsg, path = 'epubeditor/open', args = [book, temp_path, fList])

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
