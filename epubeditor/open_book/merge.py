from lxml import html, etree
from epubeditor.open_book.functions import get_files_in_spine_order
from epubeditor.open_book.files_operations import get_rel
from epubeditor.namespaces import namespaces as ns


def merge(temp_path, main_file, how_many_files):
    files_in_order = get_files_in_spine_order(temp_path)
    if how_many_files < 0 or how_many_files >= len(files_in_order):
        print("Too many files to merge!")
        return
    elif how_many_files == 0:
        how_many_files = len(files_in_order)
    
    is_main_file_found = False
    files = []
    for file in files_in_order:
        if is_main_file_found:
            if how_many_files != 0:
                files.append(file)
            else:
                break
            how_many_files -= 1
        elif file.resolve() == main_file.resolve():
            is_main_file_found = True
    
    
    main_tree = html.parse(main_file)
    main_root = main_tree.getroot()
    main_body = main_root.find('body')
    
    for file in files:
        root = html.parse(file).getroot()
        body = root.find('body')
        for child in body.getchildren():
            main_body.append(child)
    
    main_tree.write(
        main_file,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )
    
    
    # Работа с opf
    from epubeditor.editor.main import getOpf
    
    container = temp_path / 'META-INF/container.xml'
    opf = temp_path / getOpf(container)
    tree = etree.parse(opf)
    root = tree.getroot()
    
    manifest = root.find('opf:manifest', namespaces = ns)
    spine = root.find('opf:spine', namespaces = ns)
    
    for file in files:
        rel = get_rel(file, opf.parent)
        item = manifest.find(f'opf:item[@href="{rel}"]', namespaces = ns)
        itemref = spine.find(f'opf:itemref[@idref="{item.get('id')}"]', namespaces = ns)
        
        manifest.remove(item)
        spine.remove(itemref)
    
    tree.write(
        opf,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )
    
    
    # Удаление файлов
    for file in files:
        file.unlink()

def main(temp_path, arg: str):
    args = arg.strip().split()
    if len(args) != 2:
        print("Not valid args:", arg)
        return
    
    main_file = temp_path / args[0]
    if not main_file.is_file():
        print("Not valid path:", args[0])
        return
    
    try:
        how_many = int(args[1])
    except ValueError:
        print("Not valid arg:", args[1])
        return
    
    merge(temp_path, main_file, how_many)