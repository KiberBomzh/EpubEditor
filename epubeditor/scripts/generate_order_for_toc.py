from lxml import etree

from epubeditor.toc.functions import change_order


def main(temp_path):
    from epubeditor.editor.main import getOpf, getToc
    
    container = temp_path / 'META-INF/container.xml'
    opf = temp_path / getOpf(container)
    toc_tuple_str, what_is_it = getToc(opf)
    toc = (opf.parent / toc_tuple_str[0]).resolve()
    
    if what_is_it == 'nav':
        print("This script is only for .ncx TOC!")
        return
    
    tree = etree.parse(toc)
    root = tree.getroot()
    
    change_order(root)
    
    tree.write(toc, encoding = 'utf-8', xml_declaration = True, pretty_print = True)