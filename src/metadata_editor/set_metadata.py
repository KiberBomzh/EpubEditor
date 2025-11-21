from src.metadata_editor.get_metadata import getMetadataRaw
from src.metadata_editor import create_sort

from src.console_prompt import main as prompt
from src.prompt_input import input

def optionHandl(action, args):
    root = args[0]
    match action:
        case "title":
            metadata = getMetadataRaw(root)
            metadata.get('title')[0].text = input("Title", default = metadata.get('title')[0].text)
        case "author":
            metadata = getMetadataRaw(root)
            if len(metadata['creators']) > 1:
               print('There is more than one author, try "authors"') 
            else:
                metadata.get('creators')[0].text = input("Author", default = metadata.get('creators')[0].text)
        case "authors":
            metadata = getMetadataRaw(root)
            if len(metadata['creators']) > 1:
                for creator in metadata['creators']:
                    creator.text = input("Author", default = creator.text)
            else:
                print('There is only one author, try "author"') 
        case "language":
            metadata = getMetadataRaw(root)
            metadata.get('language')[0].text = input("Language", default = metadata.get('language')[0].text)
        case "series":
            metadata = getMetadataRaw(root)
            if metadata['series'] or metadata['series_index']:
                if metadata['series']:
                    series = metadata.get('series')[0]
                    if metadata['version'] == '2.0':
                        series.attrib['content'] = input("Series", default = series.attrib['content'])
                    elif metadata['version'] == '3.0':
                        series.text = input("Series", default = series.text)
                if metadata['series_index']:
                    series_index = metadata.get('series_index')[0]
                    if metadata['version'] == '2.0':
                        series_index.attrib['content'] = input("Series index", default = series_index.attrib['content'])
                    elif metadata['version'] == '3.0':
                        series_index.text = input("Series index", default = series_index.text)
            else:
                print("There's no series, try add.")
        case "sort":
            create_sort.createSort(root)
            print('Added.')
        case _:
            print("Unknown option, try again.")

def main(root, metadataRead, path):
    metaReadList = list(metadataRead.keys())
    optList = []
    for key in metaReadList:
        if '_' not in key:
            optList.append(key)
    
    help_msg = "Available options:"
    for opt in optList:
        help_msg += f"\n\t-{opt.title()}, [green]'{opt}'[/]"
    help_msg += "\n\t-Create author's sort name, print [green]'sort'[/]" + "\n\t-Go back, [green]'..'[/]" + "\n\t-Exit"
    optList.append('sort')
    optList.append('..')
    
    return prompt(optionHandl, optList, help_msg, path = path + '/set', args = [root])

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
