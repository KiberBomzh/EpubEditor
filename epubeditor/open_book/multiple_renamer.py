from lxml import etree, html
from rich.console import Console

from epubeditor.toc import sync_toc_and_nav
from epubeditor.open_book.files_operations import rename
from epubeditor.namespaces import namespaces as ns
from epubeditor.prompt_input import input

def main(temp_path):
    from epubeditor.editor.main import getOpf, getToc
            
    container = temp_path / 'META-INF/container.xml'
    opf = temp_path / getOpf(container)
    toc_tuple_str, what_is_it = getToc(opf)
    toc = (opf.parent / toc_tuple_str[0]).resolve()
    if what_is_it == 'toc':
        toc_tree = etree.parse(toc)
    elif what_is_it == 'nav':
        toc_tree = html.parse(toc)
    elif what_is_it == 'toc and nav':
        toc_tree = etree.parse(toc)
        nav = (opf.parent / toc_tuple_str[1]).resolve()
        nav_tree = html.parse(nav)
        nav_root = nav_tree.getroot()
    
    toc_root = toc_tree.getroot()
    
    tree = etree.parse(opf)
    root = tree.getroot()
    manifest = root.find('opf:manifest', namespaces = ns)
    spine = root.find('opf:spine', namespaces = ns)
    items = manifest.xpath('./opf:item', namespaces = ns)
    itemrefs = spine.getchildren()
    
    book_content = []
    for ref in itemrefs:
        for item in items:
            if ref.get('idref') == item.get('id'):
                path = opf.parent / item.get('href')
                book_content.append(path)
    name = input('File name', default = 'index_split_')
    console = Console()
    with console.status('[green]Renaming...'):
        failed_renaming = {}
        counter = 1
        for i in book_content:
            if counter < 10:
                new_name = name + f'00{counter}'
            elif counter < 100:
                new_name = name + f'0{counter}'
            else:
                new_name = name + str(counter)
            
            new_name += i.suffix
            # Если имя занято
            if not rename(i, temp_path, opf, root, new_name, toc_root):
                temp_name = i.stem + '_temp' + i.suffix
                temp_file = i.parent / temp_name
                if not temp_file.exists():
                    rename(i, temp_path, opf, root, temp_name, toc_root)
                    
                    failed_renaming[temp_file] = new_name
            
            
            counter += 1
        
        if failed_renaming:
            for key, value in failed_renaming.items():
                if not rename(key, temp_path, opf, root, value, toc_root):
                    console.log(f"Cannot rename {key.name} to {value}! The name already exists!")
    
    toc_tree.write(toc, encoding='utf-8', xml_declaration = True, pretty_print = True)
    if what_is_it == 'toc and nav':
        sync_toc_and_nav.main(toc_root, nav_root)
        nav_tree.write(nav, encoding='utf-8', pretty_print = True)
        
    tree.write(opf, encoding='utf-8', xml_declaration = True, pretty_print = True)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")