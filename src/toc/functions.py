from rich.tree import Tree
from rich import print

ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}

# Рекурсивно обходит элемент оглавления
def rec_nav(root, tree):
    points = root.xpath('./ncx:navPoint', namespaces = ns)
    if points:
        for point in points:
            label = point.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
            if label:
                if 'playOrder' in point.attrib.keys():
                    branch = tree.add(f"{label[0].text} [magenta]{point.attrib['playOrder']}[/magenta]")
                else:
                    branch = tree.add(f"{label[0].text} [magenta]{point.attrib['id']}[/magenta]")
                rec_nav(point, branch)

def ls(root):
    doc_title = root.xpath('//ncx:docTitle/ncx:text', namespaces = ns)
    if doc_title:
        print("[blue]Doc Title:[/blue]", doc_title[0].text, '\n')
    
    nav_points = root.xpath('//ncx:navMap/ncx:navPoint', namespaces = ns)
    if nav_points:
        print("[cyan]Table of contents[/cyan]")
        print("--------------------")
        for point in nav_points:
            label = point.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
            if label:
                if 'playOrder' in point.attrib.keys():
                    tree = Tree(f"{label[0].text} [magenta]{point.attrib['playOrder']}[/magenta]")
                else:
                    tree = Tree(f"{label[0].text} [magenta]{point.attrib['id']}[/magenta]")
                
                rec_nav(point, tree)
            print(tree)

def show(el):
    labelL = el.xpath('./ncx:navLabel/ncx:text/text()', namespaces = ns)
    label = labelL[0] if labelL else None
    
    print("[blue]Label:", label)
    
    print("[cyan]id:", el.attrib['id'])
    if 'playOrder' in el.attrib.keys():
        print('[cyan]playOrder:', el.attrib['playOrder'])
    
    contentL = el.xpath('./ncx:content/@src', namespaces = ns)
    content = contentL[0] if contentL else None
    
    print("[yellow]Content:", content)

def to_any_case(el, action):
    labelL = el.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
    label = labelL[0] if labelL else print(labelL)
    match action:
        case 'upper':
            label.text = label.text.upper()
        case 'lower':
            label.text = label.text.lower()
        case 'capitalize':
            label.text = label.text.capitalize()
        case 'title':
            label.text = label.text.title()

def put(root, arg):
    if ' in ' in arg:
        input_orders, destination = arg.split(' in ')
        action = 'in'
    elif ' before ' in arg:
        input_orders, destination = arg.split(' before ')
        action = 'before'
    elif ' after ' in arg:
        input_orders, destination = arg.split(' after ')
        action = 'after'
    else:
        print("Unknown option for 'put', try again.")
        return
    
    if ' ' in input_orders:
        orders = input_orders.split()
    else:
        orders = [input_orders]
    
    dests = root.xpath(f'//ncx:navPoint[@playOrder="{destination}"]', namespaces = ns)
    if not dests:
        dests = root.xpath(f'//ncx:navPoint[@id="{destination}"]', namespaces = ns)
    
    if dests:
        dest = dests[0]
        for order in orders:
            elements = root.xpath(f'//ncx:navPoint[@playOrder="{order}"]', namespaces = ns)
            if not elements:
                elements = root.xpath(f'//ncx:navPoint[@id="{order}"]', namespaces = ns)
            
            if elements:
                el = elements[0]
                
                match action:
                    case 'in':
                        dest.append(el)
                    case 'before':
                        dest.addprevious(el)
                    case 'after':
                        dest.addnext(el)

# Рекурсивно обходит все элементы и меняет playOrder
def rec_order(root, order, src_in_toc):
    points = root.xpath('./ncx:navPoint', namespaces = ns)
    if points:
        for point in points:
            order += 1
            point.attrib['playOrder'] = str(order)
            contentL = point.xpath('./ncx:content/@src', namespaces = ns)
            src_in_toc.append(contentL[0] if contentL else None)
            order = rec_order(point, order, src_in_toc)
    
    return order

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
