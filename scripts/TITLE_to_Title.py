#!/usr/bin/env -S uv run --with lxml

from lxml import html
from sys import argv
from pathlib import Path

temp_path = Path(argv[1]).resolve()
file_formats = ['.xhtml', '.html', '.htm']

for file in temp_path.rglob('*'):
    if file.is_file() and file.suffix.lower() in file_formats:
        tree = html.parse(file)
        root = tree.getroot()
        
        titles = root.xpath('//div[@class="title1"]/p')
        for t in titles:
            text = t.text
            if '. ' in text:
                new_text = ''
                sentences = text.split('. ')
                for index, sent in enumerate(sentences):
                    new_text += sent.capitalize()
                    if sentences[-1] != sent:
                        new_text += '. '
                t.text = new_text
            else:
                t.text = text.capitalize()
        
        tree.write(file, encoding='utf-8', xml_declaration = True, pretty_print = True)