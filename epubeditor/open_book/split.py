from lxml import html, etree
import copy
from epubeditor.open_book.files_operations import get_rel
from epubeditor.namespaces import namespaces as ns


split_files = []

def get_name(file, count):
    added_name = '_new_split_'
    if added_name not in file.stem:
        new_file = file.parent / f'{file.stem}_new_split_{count}{file.suffix}'
    else:
        name = file.stem
        index = name.find(added_name)
        new_name = name[:index]
        new_file = file.parent / f'{new_name}_new_split_{count}{file.suffix}'
    
    return new_file

def get_free_name(file):
    count = 1
    new_file = get_name(file, count)
    while new_file.exists():
        count += 1
        new_file = get_name(file, count)
    
    new_file.touch()
    return new_file

def rec_clean_old_and_new(old_tag, new_tag):
    # Это старый файл
    old_parent = old_tag.getparent()
    tag_siblings = old_tag.xpath('./following-sibling::*')
    for sibl in tag_siblings:
        old_parent.remove(sibl)
    
    # Это новый
    new_parent = new_tag.getparent()
    tag_siblings = new_tag.xpath('./preceding-sibling::*')
    for sibl in tag_siblings:
        new_parent.remove(sibl)
    
    if old_parent.tag != 'body' and old_parent.tag != 'body':
        rec_clean_old_and_new(old_parent, new_parent)

def split(file):
    tree = html.parse(file)
    root = tree.getroot()
    split_tags = root.xpath('//split_file_here')
    if not split_tags:
        return
    
    split_tag = split_tags[0]
    split_tag_parent = split_tag.getparent()
    
    new_tree = copy.deepcopy(tree)
    new_root = new_tree.getroot()
    
    if split_tag_parent.tag == 'body':
        new_body = new_root.find('body')
        for child in new_body.getchildren():
            new_body.remove(child)
        
        
        # Удаление с основного файла всего что идёт
        # после <split_file_here/>
        # И добавление этого в новый файл
        following_siblings = split_tag.xpath('./following-sibling::*')
        body = root.find('body')
        for sibl in following_siblings:
            new_body.append(sibl)
        
        body.remove(split_tag)
        
    else:
        new_split_tag = new_root.xpath('//split_file_here')[0]
        new_tag = new_split_tag.getparent()
        for child in new_tag.getchildren():
            new_tag.remove(child)
        
        
        following_siblings = split_tag.xpath('./following-sibling::*')
        tag = split_tag.getparent()
        for sibl in following_siblings:
            new_tag.append(sibl)
        
        tag.remove(split_tag)
        
        # Теперь в старом файле нужно удалить всё после split
        # А в новом наоборот
        rec_clean_old_and_new(tag, new_tag)
    
    new_file = get_free_name(file)
    
    new_tree.write(
        new_file,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )
    
    tree.write(
        file,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )
    
    global split_files
    split_files.append(new_file)
    
    split(new_file)

def get_id(manifest, file):
    item_id = file.name
    counter = 1
    while manifest.xpath(f'./opf:item[@id="{item_id}"]', namespaces = ns):
        item_id = f'{file.name}-{counter}'
        counter += 1
    
    return item_id

def main(temp_path, arg: str):
    # Работа с opf
    from epubeditor.editor.main import getOpf
    
    container = temp_path / 'META-INF/container.xml'
    opf = temp_path / getOpf(container)
    tree = etree.parse(opf)
    root = tree.getroot()
    
    manifest = root.find('opf:manifest', namespaces = ns)
    spine = root.find('opf:spine', namespaces = ns)
    
    if ' : ' in arg:
        files = arg.split(' : ')
    else:
        files = [arg]
    
    global split_files
    
    for file_str in files:
        file = temp_path / file_str
        if not file.is_file():
            print("Not valid path:", file)
            continue
        
        split_files.clear()
        split(file)
        
        rel = get_rel(file, opf.parent)
        item = manifest.find(f'opf:item[@href="{rel}"]', namespaces = ns)
        itemref = spine.find(f'opf:itemref[@idref="{item.get('id')}"]', namespaces = ns)
        
        for s_file in reversed(split_files):
            s_item = etree.Element('{' + ns['opf'] + '}item')
            s_item.attrib['href'] = get_rel(s_file, opf.parent)
            s_item.attrib['id'] = get_id(manifest, s_file)
            s_item.attrib['media-type'] = item.get('media-type')
            item.addnext(s_item)
            
            s_itemref = etree.Element('{' + ns['opf'] + '}itemref')
            s_itemref.attrib['idref'] = s_item.get('id')
            itemref.addnext(s_itemref)
    
    tree.write(
        opf,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )