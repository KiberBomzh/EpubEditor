from rich.tree import Tree
from rich import print
from lxml import etree
import random

from src.prompt_input import input
from src.namespaces import namespaces as ns

# Функция для простых рекурсивных обходов
def go_recursive(root, func, args = []):
    points = root.xpath('./ncx:navPoint', namespaces = ns)
    if points:
        for point in points:
            n_args = func(point, args)
            n_args = go_recursive(point, func, n_args)
        return n_args
    return args

def rec_get_orders(point, args):
    order_list = args[0]
    if 'playOrder' in point.attrib.keys():
        order = point.attrib['playOrder']
    else:
        order = point.attrib['id']
    order_list[order] = None
    return args

def rec_ls(point, args):
    tree = args[0]
    label = point.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
    if label:
        if 'playOrder' in point.attrib.keys():
            branch = tree.add(f"{label[0].text} [magenta]{point.attrib['playOrder']}[/magenta]")
        else:
            branch = tree.add(f"{label[0].text} [magenta]{point.attrib['id']}[/magenta]")
        return [branch]

def rec_change_order(point, args):
    # args[0] = order
    # args[1] = src_in_toc
    
    args[0] += 1
    point.attrib['playOrder'] = str(args[0])
    contentL = point.xpath('./ncx:content/@src', namespaces = ns)
    if contentL:
        args[1].append(contentL[0])
    return args

def get_orders(root):
    order_list = {}
    nav_points = root.xpath('//ncx:navMap/ncx:navPoint', namespaces = ns)
    if nav_points:
        for point in nav_points:
            if 'playOrder' in point.attrib.keys():
                order = point.attrib['playOrder']
            else:
                order = point.attrib['id']
            order_list[order] = None
            args = go_recursive(point, rec_get_orders, [order_list])
        order_list = args[0]
    return order_list

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
            args = go_recursive(point, rec_change_order, [order, src_in_toc])
            order = args[0]
            src_in_toc = args[1]
        return order, src_in_toc
    return 0, None

def ls(root):
    nav_points = root.xpath('//ncx:navMap/ncx:navPoint', namespaces = ns)
    if nav_points:
        for point in nav_points:
            label = point.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
            if label:
                if 'playOrder' in point.attrib.keys():
                    tree = Tree(f"{label[0].text} [magenta]{point.attrib['playOrder']}[/magenta]")
                else:
                    tree = Tree(f"{label[0].text} [magenta]{point.attrib['id']}[/magenta]")
                
                go_recursive(point, rec_ls, [tree])
            print(tree)

def show(root, sec_arg):
    elements = root.xpath(f'//ncx:navPoint[@playOrder="{sec_arg}"]', namespaces = ns)
    if elements:
        el = elements[0]
    else:
        elements = root.xpath(f'//ncx:navPoint[@id="{sec_arg}"]', namespaces = ns)
        if elements:
            el = elements[0]
        else:
            print(f"Wrong num: {sec_arg}, try again.")
            return
    
    labelL = el.xpath('./ncx:navLabel/ncx:text/text()', namespaces = ns)
    label = labelL[0] if labelL else None
    
    print("[blue]Label:", label)
    
    print("[cyan]id:", el.attrib['id'])
    if 'playOrder' in el.attrib.keys():
        print('[cyan]playOrder:', el.attrib['playOrder'])
    
    contentL = el.xpath('./ncx:content/@src', namespaces = ns)
    content = contentL[0] if contentL else None
    
    print("[yellow]Content:", content)

def to_any_case(root, action, sec_arg):
    if sec_arg is not None:
        orders = second_arg_split(sec_arg, get_orders(root))
        if orders is None:
            return
        
        for order in orders:
            elements = root.xpath(f'//ncx:navPoint[@playOrder="{order}"]', namespaces = ns)
            if elements:
                el = elements[0]
            else:
                elements = root.xpath(f'//ncx:navPoint[@id="{order}"]', namespaces = ns)
                if elements:
                    el = elements[0]
                else:
                    print(f"Wrong num: {order}.")
                    continue
            to_any_case_do(el, action)
    else:
        elements = root.xpath('//ncx:navPoint', namespaces = ns)
        for el in elements:
            to_any_case_do(el, action)

def to_any_case_do(el, action):
    labelL = el.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
    label = labelL[0] if labelL else print(labelL)
    match action:
        case 'upper':
            label.text = label.text.upper()
        case 'lower':
            label.text = label.text.lower()
        case 'capitalize':
            text = label.text
            if '. ' in text:
                new_text = ''
                sentences = text.split('. ')
                for index, sent in enumerate(sentences):
                    new_text += sent.capitalize()
                    if sentences[-1] != sent:
                        new_text += '. '
                label.text = new_text
            else:
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
        if inputs:
            return None, None, None
        else:
            return None, None
    
    if inputs:
        return input_orders, destination, action
    else:
        return destination, action

def get_orders_slice(input_orders, orders_dict):
    index = input_orders.find(':')
    start_index = input_orders[:index].rfind(' ') + 1
    end_index = input_orders[index + 1:].find(' ')
    if end_index == -1:
        end_index = len(input_orders)
    
    if index == 0 or input_orders[index - 1] == ' ':
        start = list(orders_dict.keys())[0]
    else:
        start = input_orders[start_index:index]
    include_last_el = False
    if index == len(input_orders) - 1 or input_orders[index + 1] == ' ':
        end = list(orders_dict.keys())[-1]
        include_last_el = True
    else:
        end = input_orders[index + 1:index + 1 + end_index]
    
    input_orders_left = input_orders[:start_index]
    input_orders_right = input_orders[index + 1 + end_index:]
    
    if start not in orders_dict.keys() or end not in orders_dict.keys():
        print('Error, not valid slice!')
        return None
    
    orders_iter = iter(orders_dict)
    orders_slice = []
    for o in orders_iter:
        if o == start:
            orders_slice.append(o)
            break
    
    if not orders_slice:
        print('Not found start element!')
        return None
    
    for o in orders_iter:
        if o != end:
            orders_slice.append(o)
        else:
            if include_last_el:
                orders_slice.append(o)
            break
    
    o_slice_str = ' '.join(orders_slice)
    new_input_orders = input_orders_left + o_slice_str + input_orders_right
    return new_input_orders


def second_arg_split(input_orders, orders_dict = {}):
    while ':' in input_orders:
        input_orders = get_orders_slice(input_orders, orders_dict)
        if input_orders is None:
            return None
    
    if ' ' in input_orders:
        orders = input_orders.split()
    else:
        orders = [input_orders]
    return orders

def put(root, arg):
    if any(a in arg for a in ['in', 'after', 'before']):
        input_orders, destination, action = iba_first_split(arg)
    else:
        print("Not valid action,for 'put', try with (in/before/after).")
    
    if not action:
        print("Unknown option for 'put', try again.")
        return
    
    orders = second_arg_split(input_orders, get_orders(root))
    if orders is None:
        return
    
    dests = root.xpath(f'//ncx:navPoint[@playOrder="{destination}"]', namespaces = ns)
    if not dests:
        dests = root.xpath(f'//ncx:navPoint[@id="{destination}"]', namespaces = ns)
    
    if dests:
        dest = dests[0]
        if action == 'after':
            orders = reversed(orders)
        
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
            else:
                print(f"Wrong num: {order}.")
    else:
        print(f"Wrong destination num: {destination}, try again.")

def edit(root, sec_arg):
    elements = root.xpath(f'//ncx:navPoint[@playOrder="{sec_arg}"]', namespaces = ns)
    if not elements:
        elements = root.xpath(f'//ncx:navPoint[@id="{sec_arg}"]', namespaces = ns)
    
    if elements:
        el = elements[0]
        
        labelL = el.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
        if labelL:
            label = labelL[0]
            label.text = input('Label', default = label.text)
        
        contentL = el.xpath('./ncx:content', namespaces = ns)
        if contentL:
            content = contentL[0]
            content.attrib['src'] = input('Content', default = content.get('src'))
    else:
        print(f"Wrong num: {sec_arg}, try again.")

def rm(root, sec_arg):
    orders = second_arg_split(sec_arg)
    
    for order in orders:
        elements = root.xpath(f'//ncx:navPoint[@playOrder="{order}"]', namespaces = ns)
        if elements:
            elements[0].getparent().remove(elements[0])
        else:
            elements = root.xpath(f'//ncx:navPoint[@id="{order}"]', namespaces = ns)
            if elements:
                elements[0].getparent().remove(elements[0])
            else:
                print(f"Wrong num: {order}.")

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
    
    text.text = input('Label')
    content.attrib['src'] = input('Content')
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
    else:
        print(f"Wrong destination num: {destination}, try again.")

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
