from lxml import etree, html
from pathlib import Path
import shutil

from src.toc import sync_toc_and_nav
from src.namespaces import namespaces as ns
from src.prompt_input import input

def get_relative_path(path, parent):
    path_l = str(path).split('/')
    parent_l = str(parent).split('/')
    
    equals = []
    for i, v in enumerate(path_l):
        if v == parent_l[i]:
            equals.append(i)
        else:
            break
    
    for i in reversed(equals):
        del path_l[i]
        del parent_l[i]
    
    path_str = ''
    for i in path_l:
        if i != path_l[-1]:
            path_str += i + '/'
        else:
            path_str += i
    
    for i in parent_l:
        path_str = '../' + path_str
    
    return path_str

def add(inputs, dest, manifest):
    new_files = []
    for inp in inputs:
        if Path(inp).resolve().is_file():
            path = Path(inp).resolve()
        else:
            print('Not valid path:', inp)
            return
        
        shutil.copy(path, dest)
        new_files.append(dest / path.name)
    return new_files

def add_in_manifest(new_files, manifest, root, parent):
    for file in new_files:
        item = etree.SubElement(manifest, '{' + ns['opf'] + '}item')
        try:
            item.attrib['href'] = str(file.relative_to(parent))
        except ValueError:
            item.attrib['href'] = get_relative_path(file, parent)
        item_id = file.name
        
        same_id = manifest.xpath(f'./opf:item[@id="{item_id}"]', namespaces = ns)
        counter = 1
        while same_id:
            item_id = f'{file.name}-{counter}'
            same_id = manifest.xpath(f'./opf:item[@id="{item_id}"]', namespaces = ns)
            counter += 1
        
        item.attrib['id'] = item_id
        
        m_type = get_mimetype(file.suffix.lower())
        if m_type:
            item.attrib['mime-type'] = m_type
        
        if m_type == 'application/xhtml+xml':
            add_in_spine(item_id, root)

def add_in_spine(item_id, root):
    spine = root.find('opf:spine', namespaces = ns)
    
    itemref = etree.SubElement(spine, '{' + ns['opf'] + '}itemref')
    itemref.attrib['idref'] = item_id

def get_mimetype(suffix):
    match suffix:
        case '.jpg' | '.jpeg':
            return 'image/jpeg'
        
        case '.png':
            return 'image/png'
        
        case '.xhtml' | '.html' | '.htm':
            return 'application/xhtml+xml'
        
        case '.ncx':
            return 'application/x-dtbncx+xml'
        
        case '.css':
            return 'text/css'
        
        case '.ttf':
            return 'font/ttf'
        
        case '.otf':
            return 'font/otf'
        
        case '.js':
            return 'application/javascript'
        
        case _:
            return

def rm(file, temp_path, opf, opf_root):
    # Удаление файла с манифеста
    relative_to_opf = get_rel(file, opf.parent)
    this_file = opf_root.xpath(f'//opf:item[@href="{relative_to_opf}"]', namespaces = ns)
    if this_file:
        if file.suffix.lower() in ['.xhtml', '.html', '.htm']:
            f_id = this_file[0].get('id')
        this_file[0].getparent().remove(this_file[0])
    
    match file.suffix.lower():
        case '.xhtml' | '.html' | '.htm':
            # Удаление элементов .opf которые ссылаются на файл
            refines = opf_root.xpath(f'//*[@*="{f_id}"]')
            for ref in refines:
                ref.getparent().remove(ref)
            
            rm_from_toc(file, opf)
            search_in_files(temp_path, rm_refs, file)
            
        case '.jpg' | '.jpeg' | '.png' | '.gif' | '.css':
            search_in_files(temp_path, rm_refs, file)
        case '.ttf' | '.otf':
            pass # Нахуй, потом допишу это колупание в css

def rm_from_nav(root, relative):
    elements = root.xpath(f'//a[contains(@href, "{relative}")]')
    
    for element in elements:
        li = element.getparent()
        li.remove(element)
        
        ol = li.find('ol')
        if ol is not None:
            for child in ol.getchildren():
                li.addprevious(child)
        parent_ol = li.getparent()
        parent_ol.remove(li)
        if not parent_ol.getchildren():
            parent_ol.getparent().remove(parent_ol)

def rm_from_ncx(root, relative):
    contents = root.xpath(f'//ncx:content[contains(@src, "{relative}")]', namespaces = ns)
    for content in contents:
        point = content.getparent()
        label = point.find('ncx:navLabel', namespaces = ns)
        point.remove(label)
        point.remove(content)
        
        for child in reversed(point.getchildren()):
            point.addnext(child)
        
        point.getparent().remove(point)

# Удаление файла с оглавления
def rm_from_toc(file, opf):
    from src.editor.main import getToc
    
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
    
    relative_to_toc = get_rel(file, toc.parent)
    
    if what_is_it == 'toc' or what_is_it == 'toc and nav':
        rm_from_ncx(toc_root, relative_to_toc)
        toc_tree.write(toc, encoding='utf-8', xml_declaration = True, pretty_print = True)
        if what_is_it == 'toc and nav':
            sync_toc_and_nav.main(toc_root, nav_root)
            nav_tree.write(nav, encoding='utf-8', pretty_print = True)
    elif what_is_it == 'nav':
        rm_from_nav(toc_root, relative_to_toc)
        toc_tree.write(toc, encoding='utf-8', pretty_print = True)

def search_in_files(temp_path, func, q_path, args = []):
    file_formats = ['.xhtml', '.html', '.htm']
    for file in temp_path.rglob('*'):
        if file.is_file() and file.suffix.lower() in file_formats and file != q_path:
            tree = html.parse(file)
            root = tree.getroot()
            
            relative_to_file = get_rel(q_path, file.parent)
            elements = root.xpath(f'//*[@*[contains(., "{relative_to_file}")]]')
            if elements:
                for element in elements:
                    if args:
                        func(element, args)
                    else:
                        func(element)
            
                tree.write(file, encoding='utf-8', xml_declaration = True, pretty_print = True)

def rm_refs(element):
    parent = element.getparent()
    parent.remove(element)

def rename_in_ncx(root, relative, old_name, new_name):
    contents = root.xpath(f'//ncx:content[contains(@src, "{relative}")]', namespaces = ns)
    for content in contents:
        src = content.get('src')
        content.attrib['src'] = src.replace(old_name, new_name)

def rename_in_nav(root, relative, old_name, new_name):
    hrefs = root.xpath(f'//a[contains(@href, "{relative}")]')
    for a in hrefs:
        href = a.get('href')
        a.attrib['href'] = href.replace(old_name, new_name)

def rename(file, temp_path, opf, opf_root, new_name = '', toc_root = None):
    was_new_name = True
    if not new_name:
        new_name = input('Name', default = file.stem) + file.suffix
        was_new_name = False
    
    new_file = file.parent / new_name
    if not new_file.exists():
        file.rename(new_file)
    else:
        if not was_new_name:
            print(f"{new_name} is already exists!")
        return False
    
    formats = ['.xhtml', '.html', '.htm']
    
    # Работа в .opf
    relative_to_opf = get_rel(file, opf.parent)
    this_file = opf_root.xpath(f'//opf:item[@href="{relative_to_opf}"]', namespaces = ns)
    if this_file:
        item = this_file[0]
        href = item.get('href')
        item.attrib['href'] = href.replace(file.name, new_name)
    
    # В toc.ncx
    if file.suffix.lower() in formats:
        from src.editor.main import getToc
        toc_tuple_str, what_is_it = getToc(opf)
        toc = (opf.parent / toc_tuple_str[0]).resolve()
        relative_to_toc = get_rel(file, toc.parent)
        
        if what_is_it == 'toc' or what_is_it == 'toc and nav':
            if toc_root is None:
                toc_tree = etree.parse(toc)
                toc_root = toc_tree.getroot()
                
                rename_in_ncx(toc_root, relative_to_toc, file.name, new_name)
                
                toc_tree.write(toc, encoding='utf-8', xml_declaration = True, pretty_print = True)
                
                if what_is_it == 'toc and nav':
                    nav = (opf.parent / toc_tuple_str[1]).resolve()
                    nav_tree = html.parse(nav)
                    nav_root = nav_tree.getroot()
                    sync_toc_and_nav.main(toc_root, nav_root)
                    nav_tree.write(nav, encoding='utf-8', pretty_print = True)
            else:
                # Синхронизацию дёрнуть в multiple_renamer
                rename_in_ncx(toc_root, relative_to_toc, file.name, new_name)
            
        elif what_is_it == 'nav':
            if toc_root is None:
                toc_tree = html.parse(toc)
                toc_root = toc_tree.getroot()
                
                rename_in_nav(toc_root, relative_to_toc, file.name, new_name)
                
                toc_tree.write(toc, encoding='utf-8', pretty_print = True)
            else:
                rename_in_nav(toc_root, relative_to_toc, file.name, new_name)
        
    search_in_files(temp_path, replace_name, file, args = [file.name, new_name])
    return True

def replace_name(element, args):
    old_name = args[0]
    new_name = args[1]
    for key, value in element.attrib.items():
        if old_name in value:
            element.attrib[key] = value.replace(old_name, new_name)

def get_rel(file, parent):
    try:
        rel = str(file.relative_to(parent))
    except ValueError:
        rel = get_relative_path(file, parent)
    return rel

def main(temp_path, action, arg):
    if action == 'add':
        if ' :to ' in arg:
            inp, destination = arg.split(' :to ')
            inputs = inp.split(' : ')
            dest = temp_path / destination
            if not dest.is_dir():
                print('Not valid destination path.')
                return
    
        else:
            print('Not valid arguments, try with "path/to/file :to path/to/folder"')
            return
    else:
        inputs = arg.split(' : ')
    
    from src.editor.main import getOpf
            
    container = temp_path / 'META-INF/container.xml'
    opf = temp_path / getOpf(container)
    
    tree = etree.parse(opf)
    root = tree.getroot()
    manifest = root.find('opf:manifest', namespaces = ns)
    
    match action:
        case 'add':
                new_files = add(inputs, dest, manifest)
                if new_files:
                    add_in_manifest(new_files, manifest, root, opf.parent)
        case 'rm':
            for i in inputs:
                file = temp_path / i
                if file.is_file():
                    rm(file, temp_path, opf, root)
                    file.unlink()
        case 'rename':
            for i in inputs:
                file = temp_path / i
                if file.is_file():
                    rename(file, temp_path, opf, root)
    
    tree.write(opf, encoding='utf-8', xml_declaration = True, pretty_print = True)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
