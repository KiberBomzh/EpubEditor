from rich.tree import Tree
from rich.prompt import Prompt
from rich import print
from lxml import etree
import random

ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}

# Функция для простых рекурсивных обходов
def go_recursive(root, func):
    points = root.xpath('./ncx:navPoint', namespaces = ns)
    if points:
        for point in points:
            func(point)
            go_recursive(point, func)

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

def change_order(root):
    src_in_toc = []
    nav_points = root.xpath('//ncx:navMap/ncx:navPoint', namespaces = ns)
    if nav_points:
        order = 0
        for point in nav_points:
            order += 1
            point.attrib['playOrder'] = str(order)
            contentL = point.xpath('./ncx:content/@src', namespaces = ns)
            src_in_toc.append(contentL[0] if contentL else None)
            order = rec_order(point, order, src_in_toc)
        return order, src_in_toc
    return 0, None

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

def iba_first_split(arg, inputs = True):
    if not inputs:
        arg = ' ' + arg
    
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
        return
    
    if inputs:
        return input_orders, destination, action
    else:
        return destination, action

def second_arg_split(input_orders):
    if ' ' in input_orders:
        orders = input_orders.split()
    else:
        orders = [input_orders]
    return orders

def put(root, arg):
    input_orders, destination, action = iba_first_split(arg)
    
    if not action:
        print("Unknown option for 'put', try again.")
        return
    
    orders = second_arg_split(input_orders)
    
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

def get_free_id_or_order(root, new_value, what):
    value = root.xpath(f'//ncx:navPoint[@{what}="{new_value}"]', namespaces = ns)
    counter = 1
    while value:
        new_value_mod = new_value + f'-{counter}'
        value = root.xpath(f'//ncx:navPoint[@{what}="{new_value_mod}"]', namespaces = ns)
        counter += 1
    
    return new_value if counter == 1 else new_value_mod

def create_el(root):
    point = etree.Element('{' + ns['ncx'] + '}navPoint')
    label = etree.SubElement(point, '{' + ns['ncx'] + '}navLabel')
    text = etree.SubElement(label, '{' + ns['ncx'] + '}text')
    content = etree.SubElement(point, '{' + ns['ncx'] + '}content')
    
    text.text = Prompt.ask('[green]Label[/]')
    content.attrib['src'] = Prompt.ask('[green]Content[/]')
    point.attrib['id'] = get_free_id_or_order(
        root, 
        'id' + str(random.randint(1, 1000000)), 
        'id'
    )
    point.attrib['playOrder'] = get_free_id_or_order(
        root, 
        str(random.randint(1, 1000000)), 
        'playOrder'
    )
    
    return point

def add(root, sec_arg):
    destination, action = iba_first_split(sec_arg, inputs = False)
    
    if not action:
        print("Unknown option for 'add', try again.")
        return
    
    dests = root.xpath(f'//ncx:navPoint[@playOrder="{destination}"]', namespaces = ns)
    if not dests:
        dests = root.xpath(f'//ncx:navPoint[@id="{destination}"]', namespaces = ns)
    
    if dests:
        dest = dests[0]
        point = create_el(root)
        
        match action:
            case 'in':
                dest.append(point)
            case 'before':
                dest.addprevious(point)
            case 'after':
                dest.addnext(point)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
