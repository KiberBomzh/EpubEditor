from lxml import etree, html
from pathlib import Path
import shutil
from prompt_toolkit import prompt as input
from rich import print
from src.namespaces import namespaces as ns
from src.console_prompt import style

def add(inputs, dest, manifest):
    new_files = []
    for inp in inputs:
        path = validate_path_add(inp)
        if not path:
            print('Not valid path:', inp)
            return
        shutil.copy(path, dest)
        new_files.append(dest / path.name)
    return new_files

def add_in_manifest(new_files, manifest, parent):
    for file in new_files:
        item = etree.SubElement(manifest, '{' + ns['opf'] + '}item')
        item.attrib['href'] = str(file.relative_to(parent))
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

def validate_path_add(path):
    if path[:2] == '~/':
        if Path.home() / path[2:].is_file():
            return Path.home() / path[2:]
    
    elif Path(path).resolve().is_file():
        return Path(path).resolve()

def rm(file, temp_path, opf, opf_root):
    # Удаление файла с манифеста
    this_file = opf_root.xpath(f'//opf:item[contains(@href, "{file.name}")]', namespaces = ns)
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

# Удаление файла с оглавления
def rm_from_toc(file, opf):
    from src.editor.main import getToc
    
    toc = opf.parent / getToc(opf)
    toc_tree = etree.parse(toc)
    toc_root = toc_tree.getroot()
    
    contents = toc_root.xpath(f'//ncx:content[contains(@src, "{file.name}")]', namespaces = ns)
    for content in contents:
        point = content.getparent()
        label = point.find('ncx:navLabel', namespaces = ns)
        point.remove(label)
        point.remove(content)
        
        for child in reversed(point.getchildren()):
            print(child.attrib['playOrder'])
            point.addnext(child)
        
        point.getparent().remove(point)
    
    toc_tree.write(toc, encoding='utf-8', xml_declaration = True, pretty_print = True)

def search_in_files(temp_path, func, q_path, args = []):
    file_formats = ['.xhtml', '.html', '.htm']
    for file in temp_path.rglob('*'):
        if file.is_file() and file.suffix.lower() in file_formats and file != q_path:
            tree = html.parse(file)
            root = tree.getroot()
            
            elements = root.xpath(f'//*[@*[contains(., "{q_path.name}")]]')
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

def rename(file, temp_path, opf, opf_root):
    print('[blue]Name')
    new_name = input('> ', default = file.stem, style = style) + file.suffix
    formats = ['.xhtml', '.html', '.htm']
    
    # Работа в .opf
    this_file = opf_root.xpath(f'//opf:item[contains(@href, "{file.name}")]', namespaces = ns)
    if this_file:
        item = this_file[0]
        href = item.get('href')
        item.attrib['href'] = href.replace(file.name, new_name)
    
    # В toc.ncx
    if file.suffix.lower() in formats:
        rename_in_toc(file.name, new_name, opf)
            
    search_in_files(temp_path, replace_name, file, args = [file.name, new_name])
    
    new_file = file.parent / new_name
    file.rename(new_file)

def rename_in_toc(old_name, new_name, opf):
    from src.editor.main import getToc
    
    toc = opf.parent / getToc(opf)
    toc_tree = etree.parse(toc)
    toc_root = toc_tree.getroot()
    
    contents = toc_root.xpath(f'//ncx:content[contains(@src, "{old_name}")]', namespaces = ns)
    for content in contents:
        src = content.get('src')
        content.attrib['src'] = src.replace(old_name, new_name)
    
    toc_tree.write(toc, encoding='utf-8', xml_declaration = True, pretty_print = True)

def replace_name(element, args):
    old_name = args[0]
    new_name = args[1]
    for key, value in element.attrib.items():
        if old_name in value:
            element.attrib[key] = value.replace(old_name, new_name)

def main(temp_path, action, arg):
    if action == 'add':
        if ' to ' in arg:
            inp, destination = arg.split(' to ')
            inputs = inp.split()
            dest = temp_path / destination
            if not dest.is_dir():
                print('Not valid destination path.')
                return
    
        else:
            print('Not valid arguments, try with "file to folder"')
            return
    else:
        inputs = arg.split()
    
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
                    add_in_manifest(new_files, manifest, opf.parent)
        case 'rm':
            for i in inputs:
                file = temp_path / i
                if file.is_file():
                    rm(file, temp_path, opf, root)
                    file.unlink()
        case 'rename':
            file = temp_path / inputs[0]
            if file.is_file():
                rename(file, temp_path, opf, root)
    
    tree.write(opf, encoding='utf-8', xml_declaration = True, pretty_print = True)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
