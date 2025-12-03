from lxml import html
from src.toc.nav_functions import get_nav
from src.namespaces import namespaces as ns

def recursive(toc, nav):
    points = toc.xpath('./ncx:navPoint', namespaces = ns)
    if points:
        ol = html.Element('ol')
        nav.append(ol)
    
    for point in points:
        label_raw = point.xpath('./ncx:navLabel/ncx:text/text()', namespaces = ns)
        src_raw = point.xpath('./ncx:content/@src', namespaces = ns)
        label = label_raw[0] if label_raw else None
        src = src_raw[0] if src_raw else None
        
        li = html.Element('li')
        ol.append(li)
        
        a = html.Element('a')
        li.append(a)
        
        a.text = label
        a.attrib['href'] = src
        
        recursive(point, li)

def main(toc_root, nav_root):
    nav_map = toc_root.find('ncx:navMap', namespaces = ns)
    nav = get_nav(nav_root)
    for child in nav.getchildren():
        nav.remove(child)
    
    recursive(nav_map, nav)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
