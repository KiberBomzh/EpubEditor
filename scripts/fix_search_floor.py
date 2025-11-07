#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "lxml",
# ]
# ///
from sys import argv
from pathlib import Path
from lxml import html

temp_path = Path(argv[1]).resolve()
file_formats = ['.xhtml', '.html', '.htm']
old_value = '⁈'
new_value = '?!'
file_counter = 0
p_counter = 0

for file in temp_path.rglob('*'):
    if file.is_file() and file.suffix.lower() in file_formats:
        tree = html.parse(file)
        root = tree.getroot()
        
        paragraphs = root.xpath(f'//p[contains(text(), "{old_value}")]')
        if not paragraphs:
            paragraphs = root.xpath(f'//div[contains(text(), "{old_value}")]')
        
        if paragraphs:
            for p in paragraphs:
                p.text = p.text.replace(old_value, new_value)
                p_counter += 1
            file_counter += 1
        
            tree.write(file, encoding='utf-8', xml_declaration = True, pretty_print = True)

print('--------------------------')
print(f'Файлов пройдено: {file_counter}')
print(f'Параграфов пройдено: {p_counter}')
print('--------------------------')
