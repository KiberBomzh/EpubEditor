#!/usr/bin/env python

# This is an example script for the flag "--script"

from sys import argv
from pathlib import Path


temp_path = Path(argv[1]).resolve()
file_formats = ['.xhtml', '.html', '.htm']
old_value = '⁈'
new_value = '?!'
file_counter = 0

for file in temp_path.rglob('*'):
    if file.is_file() and file.suffix.lower() in file_formats:
        file.write_text(file.read_text().replace(old_value, new_value))
        file_counter += 1
    
print('--------------------------')
print(f'Файлов пройдено: {file_counter}')
print('--------------------------')
