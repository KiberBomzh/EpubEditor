from lxml import etree

from src.metadata_editor.get_metadata import getMetadataRaw
from src.namespaces import namespaces

def get_free_id(metadata, Id):
    new_id = Id
    count = 1
    while metadata.find(f'*[@id="{new_id}"]') is not None:
        new_id = f'{Id}-{count}'
        count += 1
    
    return new_id

def createSort(root):
    metadata = getMetadataRaw(root)
    if metadata['version'] == '2.0':
        if metadata['title']:
            title = metadata['title'][0].text
            wordList = title.split()
            if len(wordList) > 1:
                first = wordList[0].lower()
                if first == 'the' or first == 'a' or first == 'an':
                    art = wordList.pop(0)
                    wordList[-1] += ','
                    wordList.append(art)
                    title_sort = ' '.join(wordList)
                else:
                    title_sort = title
            else:
                title_sort = title
            
            title_as = root.xpath('//opf:meta[@name="calibre:title_sort"]', namespaces = namespaces)
            if title_as:
                title_as[0].set('content', title_sort)
            else:
                title_as = etree.Element('{' + namespaces['opf'] + '}meta')
                title_as.set('name', 'calibre:title_sort')
                title_as.set('content', title_sort)
                metadata['metadata'].append(title_as)
        
        if len(metadata['creators']) > 1:
            for creator in metadata['creators']:
                author = creator.text
                wordList = author.split()
                if len(wordList) > 1:
                    lastWord = wordList.pop()
                    wordList.insert(0, f"{lastWord},")
                    author_sort = ' '.join(wordList)
                else:
                    author_sort = author
                creator.set('{' + namespaces["opf"] + '}file-as', author_sort)
        elif len(metadata['creators']) == 1:
            author = metadata.get('creators')[0].text
            wordList = author.split()
            if len(wordList) > 1:
                lastWord = wordList.pop()
                wordList.insert(0, f"{lastWord},")
                author_sort = ' '.join(wordList)
            else:
                author_sort = author
            metadata.get('creators')[0].set('{' + namespaces["opf"] + '}file-as', author_sort)
    elif metadata['version'] == '3.0':
        if metadata['title']:
            title = metadata['title'][0].text
            wordList = title.split()
            if len(wordList) > 1:
                first = wordList[0].lower()
                if first == 'the' or first == 'a' or first == 'an':
                    art = wordList.pop(0)
                    wordList[-1] += ','
                    wordList.append(art)
                    title_sort = ' '.join(wordList)
                else:
                    title_sort = title
            else:
                title_sort = title
            
            t_id = metadata['title'][0].get('id')
            if t_id is None:
                new_id = get_free_id(metadata['metadata'], 'title')
                metadata['title'][0].attrib['id'] = new_id
                titleId = '#' + new_id
            else:
                titleId = '#' + t_id
            
            title_as = root.xpath(f'//opf:meta[@refines="{titleId}" and @property="file-as"]', namespaces = namespaces)
            
            if title_as:
                title_as[0].text = title_sort
            else:
                title_as = etree.Element('{' + namespaces['opf'] + '}meta')
                title_as.set('refines', titleId)
                title_as.set('property', 'file-as')
                title_as.text = title_sort
                metadata['metadata'].append(title_as)
        
        if len(metadata['creators']) > 1:
            for creator in metadata['creators']:
                a_id = creator.get('id')
                if a_id is None:
                    new_id = get_free_id(metadata['metadata'], 'author')
                    creator.attrib['id'] = new_id
                    authorId = '#' + new_id
                else:
                    authorId = '#' + a_id
                
                author_as = root.xpath(f'//opf:meta[@refines="{authorId}" and @property="file-as"]', namespaces = namespaces)
                if author_as:
                    author = creator.text
                    wordList = author.split()
                    if len(wordList) > 1:
                        lastWord = wordList.pop()
                        wordList.insert(0, f"{lastWord},")
                        author_sort = ' '.join(wordList)
                    else:
                        author_sort = author
                    author_as[0].text = author_sort
                else:
                    author = creator.text
                    wordList = author.split()
                    if len(wordList) > 1:
                        lastWord = wordList.pop()
                        wordList.insert(0, f"{lastWord},")
                        author_sort = ' '.join(wordList)
                    else:
                        author_sort = author
                    author_as = etree.Element('{' + namespaces['opf'] + '}meta')
                    author_as.set('refines', authorId)
                    author_as.set('property', 'file-as')
                    author_as.text = author_sort
                    metadata['metadata'].append(author_as)
        elif len(metadata['creators']) == 1:
            a_id = metadata['creators'][0].get('id')
            if a_id is None:
                new_id = get_free_id(metadata['metadata'], 'author')
                metadata['creators'][0].attrib['id'] = new_id
                authorId = '#' + new_id
            else:
                authorId = '#' + a_id
            
            author_as = root.xpath(f'//opf:meta[@refines="{authorId}" and @property="file-as"]', namespaces = namespaces)
            if author_as:
                author = metadata.get('creators')[0].text
                wordList = author.split()
                if len(wordList) > 1:
                    lastWord = wordList.pop()
                    wordList.insert(0, f"{lastWord},")
                    author_sort = ' '.join(wordList)
                else:
                    author_sort = author
                author_as[0].text = author_sort
            else:
                author = metadata.get('creators')[0].text
                wordList = author.split()
                if len(wordList) > 1:
                    lastWord = wordList.pop()
                    wordList.insert(0, f"{lastWord},")
                    author_sort = ' '.join(wordList)
                else:
                    author_sort = author
                author_as = etree.Element('{' + namespaces['opf'] + '}meta')
                author_as.set('refines', authorId)
                author_as.set('property', 'file-as')
                author_as.text = author_sort
                metadata['metadata'].append(author_as)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
