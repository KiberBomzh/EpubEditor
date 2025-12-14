#!/usr/bin/env -S uv run --with lxml

from lxml import html
from pathlib import Path
from sys import argv

def capitalize(text):
    new_text = ''
    if '. ' in text:
        sentences = text.split('. ')
        for index, sent in enumerate(sentences):
            new_text += sent.capitalize()
            if sentences[-1] != sent:
                new_text += '. '
    else:
        new_text = text.capitalize()
    
    return new_text

def main(temp_path, query):
    file_formats = ['.xhtml', '.html', '.htm']
    
    for file in temp_path.rglob('*'):
        if file.is_file() and file.suffix.lower() in file_formats:
            tree = html.parse(file)
            root = tree.getroot()
            
            titles = root.xpath(query)
            for t in titles:
                t.text = capitalize(t.text)
            
            tree.write(file, encoding='utf-8', xml_declaration = True, pretty_print = True)

if __name__ == '__main__':
    temp_path = Path(argv[1])
    query = '//div[@class="title1"]/p'
    main(temp_path, query)