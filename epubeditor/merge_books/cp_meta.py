from lxml import etree, html
from pathlib import Path

from epubeditor.open_book.files_operations import get_rel
from epubeditor.metadata_editor.create_sort import get_free_id
from epubeditor.namespaces import namespaces as ns


def get_path_rel_to_root(path: str, parent: Path, root_path: Path, num: str):
    rel_path = (parent / path).resolve()
    new_path = num + '/' + get_rel(rel_path, root_path)
    return new_path

def cp_opf(main_opf, opf, num, parent_for_all):
    main_tree = etree.parse(main_opf)
    main_root = main_tree.getroot()
    
    main_manifest = main_root.find('opf:manifest', namespaces = ns)
    main_spine = main_root.find('opf:spine', namespaces = ns)
    
    
    root = etree.parse(opf).getroot()
    manifest = root.find('opf:manifest', namespaces = ns)
    spine = root.find('opf:spine', namespaces = ns)
    
    items = manifest.xpath('./opf:item', namespaces = ns)
    old_id = {}
    for item in items:
        if item.get('href').endswith('.ncx'):
            continue
        
        new_item = etree.SubElement(main_manifest, '{%s}item' % ns['opf'])
        href = get_path_rel_to_root(
            item.get('href'),
            opf.parent,
            parent_for_all,
            num
        )
        new_item.attrib['href'] = href
        
        # Запоминаем старое id для spine
        i_id = item.get('id')
        old_id[i_id] = new_item
        new_item.attrib['id'] = get_free_id(main_manifest, num + '-' + Path(href).name)
        
        new_item.attrib['media-type'] = item.get('media-type')
    
    itemrefs = spine.xpath('./opf:itemref', namespaces = ns)
    for ref in itemrefs:
        new_ref = etree.SubElement(main_spine, '{%s}itemref' % ns['opf'])
        
        r_id = ref.get('idref')
        r_item = old_id[r_id]
        new_ref.attrib['idref'] = r_item.get('id')
    
    
    main_tree.write(
        main_opf,
        xml_declaration = True,
        encoding = 'UTF-8'
    )

def cp_from_toc(main_root, root, toc, num, parent_for_all):
    main_nav_map = main_root.find('ncx:navMap', namespaces = ns)
    nav_map = root.find('ncx:navMap', namespaces = ns)
    
    links = root.xpath('//ncx:navPoint/ncx:content', namespaces = ns)
    for link in links:
        src = get_path_rel_to_root(
            link.get('src'),
            toc.parent,
            parent_for_all,
            num
        )
        link.attrib['src'] = src
    
    for child in nav_map.getchildren():
        main_nav_map.append(child)


def create_point(parent, li):
    point = etree.SubElement(parent, '{%s}navPoint' % ns['ncx'])
    label = etree.SubElement(point, '{%s}navLabel' % ns['ncx'])
    text = etree.SubElement(label, '{%s}text' % ns['ncx'])
    a = li.find('a')
    text.text = a.text
    content = etree.SubElement(point, '{%s}content' % ns['ncx'])
    content.attrib['src'] = a.get('href')
    
    return point
    
def rec_nav_to_toc(nav_root, toc_root):
    nav_li = nav_root.xpath('./ol/li')
    for li in nav_li:
        point = create_point(toc_root, li)
        rec_nav_to_toc(li, point)

def cp_from_nav(main_root, root, toc, num, parent_for_all):
    nav = root.find('.//nav[@id="toc"]')
    nav_map = main_root.find('ncx:navMap', namespaces = ns)
    
    links = root.xpath('//li/a')
    for link in links:
        href = get_path_rel_to_root(
            link.get('href'),
            toc.parent,
            parent_for_all,
            num
        )
        link.attrib['href'] = href
    
    
    rec_nav_to_toc(nav, nav_map)

def cp_toc(main_toc, toc, what_is_it, num, parent_for_all):
    main_tree = etree.parse(main_toc)
    main_root = main_tree.getroot()
    
    
    if what_is_it in ['toc', 'toc and nav']:
        root = etree.parse(toc)
        cp_from_toc(main_root, root, toc, num, parent_for_all)
    elif what_is_it == 'nav':
        root = html.parse(toc)
        cp_from_nav(main_root, root, toc, num, parent_for_all)
    
    
    main_tree.write(
        main_toc,
        xml_declaration = True,
        encoding = 'UTF-8'
    )
