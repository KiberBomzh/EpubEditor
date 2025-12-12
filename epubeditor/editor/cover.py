from lxml import etree
import zipfile
import tempfile
import subprocess
from pathlib import Path
from prompt_toolkit.completion import NestedCompleter, PathCompleter

from epubeditor.console_prompt import main as prompt
from epubeditor.namespaces import namespaces

# Возвращает название обложки в книге
def getCover(book):
    with zipfile.ZipFile(book, 'r') as book_r:
        for file in book_r.namelist():
            if file.endswith('.opf'):
                opf_file = file
        with book_r.open(opf_file) as opf:
            root = etree.parse(opf).getroot()
        
        coverId = root.xpath('//opf:meta[@name="cover"]/@content', namespaces = namespaces)
        if coverId:
            coverId = coverId[0]
            cover_in_book = root.xpath(f'//opf:item[@id="{coverId}"]/@href', namespaces = namespaces)
            if cover_in_book:
                cover_in_book = cover_in_book[0]
                fileList = book_r.namelist()
                for i, file in enumerate(fileList):
                    if cover_in_book in file:
                        cover_in_book = file
                return cover_in_book
            else:
                print('Metadata error!')
        else:
            return False

def changeCover(book, cover):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        cib = getCover(book)
        if cib:
            cover_in_book = temp_path / Path(cib)
            cib_parents = cover_in_book.parents[0]
            if not cib_parents.exists():
                cib_parents.mkdir(parents = True)
            
            if cover_in_book.suffix.lower() == cover.suffix.lower():
                cover_in_book = cover_in_book.relative_to(temp_path)
                subprocess.run(f"cd {temp_path} && cp {cover} {cover_in_book} && zip -u '{book}' {cover_in_book}", shell = True)
            else:
                print(f"Formats {cover_in_book.name} and {cover.name} isn't the same!")
        else:
            print("There's no cover in the book, try add.")

def addCover(book, cover):
    if getCover(book):
        print("There's already cover in the book, try set.")
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            with zipfile.ZipFile(book, 'r') as book_r:
                for file in book_r.namelist():
                    if file.endswith('.opf'):
                        opf_file = file
                book_r.extract(opf_file, temp_path)
                
            opf = list(temp_path.rglob('*.opf'))[0]
            tree = etree.parse(opf)
            root = tree.getroot()
            
            metadata = root.xpath('//opf:metadata', namespaces = namespaces)
            manifest = root.xpath('//opf:manifest', namespaces = namespaces)
            
            if metadata and manifest:
                metadata = metadata[0]
                manifest = manifest[0]
                subprocess.run(["cp", cover, opf.parent])
                cover_in_temp = opf.parent / cover.name
                cover_rel_to_temp = cover_in_temp.relative_to(temp_path)
                cover_rel_to_opf = cover_in_temp.relative_to(opf.parent)
                if cover_in_temp.suffix.lower() == '.png':
                    m_type = 'image/png'
                elif cover_in_temp.suffix.lower() == '.jpg' or cover_in_temp.suffix.lower() == '.jpeg':
                    m_type = 'image/jpeg'
                
                metaCover = etree.SubElement(metadata, 'meta')
                coverId = "cover"
                metaCover.attrib['name'] = "cover"
                metaCover.attrib['content'] = coverId
                
                manifestCover = etree.SubElement(manifest, 'item')
                manifestCover.attrib['id'] = coverId
                manifestCover.attrib['href'] = str(cover_rel_to_opf)
                manifestCover.attrib['media-type'] = m_type
                
                tree.write(opf, encoding='utf-8', xml_declaration = True, pretty_print = True)
                
                subprocess.run(f"cd {temp_path} && zip -u '{book}' '{cover_rel_to_temp}' '{opf.relative_to(temp_path)}'", shell = True)
            else:
                print("Error, there's no metadata or manifest!")

def extractCover(book, outpath):
    cover_in_book = getCover(book)
    if cover_in_book:
        out_cover = outpath / Path(cover_in_book).name
        new_cover_name = book.stem + out_cover.suffix
        new_cover = outpath / new_cover_name
        subprocess.run(f'unzip -p "{book}" "{cover_in_book}" > "{new_cover}"', shell = True)
    else:
        print("There's no cover in the book!")
    

def optionHandl(action, args, cover = ''):
    book = args[0]
    if cover:
        cover = Path(cover.strip())
        cover = cover.resolve()
        if validateCover(cover):
            changeCover(book, cover)
        else:
            print("Not valid cover, try another.")
    else:
        if len(args) > 1:
            cover_path = Path(args[1].strip()).resolve()
            
            match action:
                case 'set':
                    if validateCover(cover_path):
                        changeCover(book, cover_path)
                    else:
                        print("Not valid cover, try another.")
                case 'add':
                    if validateCover(cover_path):
                        addCover(book, cover_path)
                    else:
                        print("Not valid cover, try another.")
                case 'extract':
                    if cover_path.is_dir():
                        extractCover(book, cover_path)
                    else:
                        print("Extract path isn't existing!")
                case _:
                    print('Unknown option, try again.')
        else:
            print("Not valid second argument, try another.")
        

def validateCover(cover_path):
    if cover_path.is_file():
        allowed_formats = ['.jpg', '.jpeg', '.png']
        if cover_path.suffix in allowed_formats:
            return True
    return False

def main(book):
    help_msg = ("Available options:\n" +
        "\t-Set         'set path/to/cover'\n" +
        "\t-Add         'add path/to/cover'\n" +
        "\t-Extract     'extract output/path'\n" +
        "\t-Go back      '..'\n" +
        "\t-Exit")
    
    path_completer = PathCompleter(
        expanduser=True,  # Раскрывать ~ в домашнюю директорию
        file_filter=lambda name: '.' != Path(name).stem[0],
        min_input_len=0,  # Показывать сразу
        get_paths=lambda: ['.'],
    )
    completer = NestedCompleter.from_nested_dict({
        'set': path_completer,
        'add': path_completer,
        'extract': path_completer,
        'help': None,
        '..': None,
        'exit': None
    })
    return prompt(optionHandl, completer, help_msg, path = 'epubeditor/cover', args = [book])

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
