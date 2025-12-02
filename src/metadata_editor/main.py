from lxml import etree
from prompt_toolkit.completion import NestedCompleter

from src.metadata_editor import get_metadata, set_metadata, add_metadata, remove_metadata, create_sort
from src.console_prompt import main as prompt

def optionHandl(action, args):
    root = args[0]
    second_arg = args[1].strip() if len(args) > 1 else None
    
    match action:
        case "print":
            get_metadata.getMetadata(root, Print = True)
        case "set":
            set_metadata.main(second_arg, root)
        case "add":
            add_metadata.main(second_arg, root)
        case "rm":
            remove_metadata.main(second_arg, root)
        case "sort":
            create_sort.createSort(root)
        case _:
            print("Unknown option, try again.")



def main(opf, path = 'epubeditor/meta'):
    tree = etree.parse(opf)
    root = tree.getroot()
    help_msg = ("Available options:\n" +
            "\t-Set                 [green]'set command'[/]\n" + 
            "\t-Add                 [green]'add command'[/]\n" +
            "\t-Remove              [green]'rm command'[/]\n" +
            "\t-Print               [green]'print'[/]\n" +
            "\t-Create sort names   [green]'sort'[/]\n" +
            "\t-Go back             [green]'..'[/]\n" +
            "\t-Exit")
    
    keys = {}
    metadataRead = get_metadata.getMetadata(root)
    for key in metadataRead.keys():
        if '_' not in key:
            keys[key] = None
    keys['help'] = None
    
    completer = NestedCompleter.from_nested_dict({
        'set': keys,
        'add': {
            'title': None,
            'author': None,
            'series': None,
            'language': None,
            'help': None,
        },
        'rm': keys,
        'sort': None,
        'print': None,
        '..': None,
        'exit': None,
        'help': None,
    })
    
    act = prompt(optionHandl, completer, help_msg, path = path, args = [root])
    tree.write(opf, encoding = 'utf-8', xml_declaration = True, pretty_print = True)
    return act

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
