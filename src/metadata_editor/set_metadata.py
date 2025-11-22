from rich import print

from src.metadata_editor.get_metadata import getMetadataRaw, getMetadata
from src.prompt_input import input

def print_help(metadataRead):
    metaReadList = list(metadataRead.keys())
    print("Available options:")
    for key in metaReadList:
        if '_' not in key:
            print(f"\t-{key.title()}, [green]'{key}'[/]")


def main(action, root):
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
        case "help":
            print_help(getMetadata(root))
        case _:
            print("Unknown option for set, try 'set help'")

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
