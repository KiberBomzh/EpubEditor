from lxml import etree

from src.metadata_editor import get_metadata, set_metadata, add_metadata, remove_metadata
from src.console_prompt import main as prompt

def optionHandl(action, args):
    root = args[0]
    path = args[1]
    metadataRead = get_metadata.getMetadata(root)
    
    match action:
        case "print":
            get_metadata.getMetadata(root, Print = True)
        case "set":
            return set_metadata.main(root, metadataRead, path)
        case "add":
            return add_metadata.main(root, path)
        case "remove":
            return remove_metadata.main(root, metadataRead, path)
        case _:
            print("Unknown option, try again.")

def main(opf, path = 'epubeditor/meta'):
    tree = etree.parse(opf)
    root = tree.getroot()
    help_msg = ("Available options:\n" +
            "\t-Set\n" + 
            "\t-Add\n" +
            "\t-Remove\n" +
            "\t-Print\n" +
            "\t-Go back, '..'\n" +
            "\t-Exit")
    optList = ['set', 'add', 'remove', 'print', '..']
    act = prompt(optionHandl, optList, help_msg, path = path, args = [root, path])
    tree.write(opf, encoding='utf-8', xml_declaration = True, pretty_print = True)
    return act

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
