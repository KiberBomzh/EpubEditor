from lxml import etree
from rich.prompt import Prompt
from rich import print

from src.console_prompt import main as prompt
from src.toc.functions import ls, show, to_any_case, put, rec_order
from src.toc.sort_spine import main as sort_spine

ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}

def optionHandl(action, args):
    root = args[0]
    if len(args) > 1:
        sec_arg = args[1]
    else:
        sec_arg = None
    
    match action:
        case 'ls':
            ls(root)
        case 'show':
            if sec_arg:
                elements = root.xpath(f'//ncx:navPoint[@playOrder="{sec_arg}"]', namespaces = ns)
                if elements:
                    el = elements[0]
                    show(el)
                else:
                    elements = root.xpath(f'//ncx:navPoint[@id="{sec_arg}"]', namespaces = ns)
                    if elements:
                        el = elements[0]
                        show(el)
            else:
                print('Option needs second argument, try again.')
        case 'edit':
            if sec_arg:
                elements = root.xpath(f'//ncx:navPoint[@playOrder="{sec_arg}"]', namespaces = ns)
                if not elements:
                    elements = root.xpath(f'//ncx:navPoint[@id="{sec_arg}"]', namespaces = ns)
                
                if elements:
                    el = elements[0]
                    labelL = el.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
                    label = labelL[0] if labelL else print(labelL)
                    print('[blue]Old label:[/blue]', label.text)
                    new_label = Prompt.ask('[green]New label')
                    if new_label:
                        label.text = new_label
            else:
                print('Option needs second argument, try again.')
        case 'put':
            if sec_arg:
                put(root, sec_arg)
            else:
                print('Option needs second argument, try again.')
        case 'upper' | 'lower' | 'capitalize' | 'title':
            if sec_arg:
                if ' ' in sec_arg:
                    orders = sec_arg.split()
                else:
                    orders = [sec_arg]
                
                for order in orders:
                    elements = root.xpath(f'//ncx:navPoint[@playOrder="{order}"]', namespaces = ns)
                    if elements:
                        to_any_case(elements[0], action)
                    else:
                        elements = root.xpath(f'//ncx:navPoint[@id="{order}"]', namespaces = ns)
                        if elements:
                            to_any_case(elements[0], action)
                    
            else:
                elements = root.xpath('//ncx:navPoint', namespaces = ns)
                for el in elements:
                    to_any_case(el, action)
        case _:
            print("Unknown option, try again.")

def main(toc, opf, path = 'epubeditor/toc'):
    toc_tree = etree.parse(toc)
    toc_root = toc_tree.getroot()
    opf_tree = etree.parse(opf)
    opf_root = opf_tree.getroot()
    help_msg = ("Available options:\n" +
            "\t-ls, show all elements\n" + 
            "\t-show playOrder, show element\n" + 
            "\t-edit playOrder, edit element's label\n" + 
            "\t-put playOrders [in/before/after] playOrder\n" + 
            "\t-upper, change case for playOrder or for all\n" +
            "\t-lower, change case for playOrder or for all\n" +
            "\t-capitalize, change case for playOrder or for all\n" +
            "\t-title, change case for playOrder or for all\n" +
            "\t-Go back, '..'\n" +
            "\t-Exit")
    optList = ['ls', 'show', 'edit', 'put', 'upper', 'lower', 'capitalize', 'title', '..']
    act = prompt(optionHandl, optList, help_msg, path = path, args = [toc_root])
    
    src_in_toc = []
    nav_points = toc_root.xpath('//ncx:navMap/ncx:navPoint', namespaces = ns)
    if nav_points:
        order = 0
        for point in nav_points:
            order += 1
            point.attrib['playOrder'] = str(order)
            contentL = point.xpath('./ncx:content/@src', namespaces = ns)
            src_in_toc.append(contentL[0] if contentL else None)
            order = rec_order(point, order, src_in_toc)
    if order > 0:
        sort_spine(opf_root, src_in_toc)
    
    toc_tree.write(toc, encoding='utf-8', xml_declaration = True, pretty_print = True)
    opf_tree.write(opf, encoding='utf-8', xml_declaration = True, pretty_print = True)
    return act

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
