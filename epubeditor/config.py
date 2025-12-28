import tomllib
from pathlib import Path
import os

from rich import print


from epubeditor.cli import args


# Глобальный переменные
replacement_for_forbidden_chars = '_'


# [scripts]
script_path = ''


# split_by_titles
clean_body_attributes = True


# toc_from titles
include_subtitles = False
all_h = False
only_h = False


# [open]
autosave = False


# [sort]
# sort.py
main_path = None
search_empty_folders = True
sort_template = [
    '{authors1}',
    '{series}',
    '{index/ - }{title}'
]

# book_renamer.py
name_template = '{authors&/ - }{series/ <index*(|)/, >}{title}'

# template_handler
index_template = ''


HOME = os.getenv('HOME', str(Path.home())) + '/.config'
config_home = os.getenv('XDG_CONFIG_HOME', HOME)

config_path = 'epubeditor/config.toml'
config_file = Path(config_home) / config_path

if config_file.exists() and not args.ignore_config:
    try:
        with open(config_file, 'rb') as f:
            config = tomllib.load(f)
        
        
        if 'replacement_for_forbidden_chars' in config:
            replacement_for_forbidden_chars = config['replacement_for_forbidden_chars']
        
        
        if 'scripts' in config:
            if 'path' in config['scripts']:
                script_path = config['scripts']['path']
                if '~/' in script_path:
                    script_path = os.path.expanduser(script_path)
            
            
            if 'split_by_titles' in config['scripts']:
                split_by_titles_flags = {}
                for flag in config['scripts']['split_by_titles']:
                    split_by_titles_flags.update(flag)
                
                if 'clean_body_attributes' in split_by_titles_flags:
                    clean_body_attributes = split_by_titles_flags['clean_body_attributes']

            
            if 'toc_from_titles' in config['scripts']:
                toc_from_titles_flags = {}
                for flag in config['scripts']['toc_from_titles']:
                    toc_from_titles_flags.update(flag)
            
                if 'include_subtitles' in toc_from_titles_flags:
                    include_subtitles = toc_from_titles_flags['include_subtitles']
                
                if 'all_h' in toc_from_titles_flags:
                    all_h = toc_from_titles_flags['all_h']
    
                if 'only_h' in toc_from_titles_flags:
                    only_h = toc_from_titles_flags['only_h']

        
        
        if 'open' in config:
            if 'autosave' in config['open']:
                autosave = config['open']['autosave']
        
        
        if 'sort' in config:
            if 'main_path' in config['sort']:
                main_path = config['sort']['main_path']
    
            if 'search_empty_folders' in config['sort']:
                search_empty_folders = config['sort']['search_empty_folders']
            
            if 'sort_template' in config['sort']:
                sort_template = config['sort']['sort_template']
            
            
            if 'rename_template' in config['sort']:
                name_template = config['sort']['rename_template']
            
            
            if 'series_index_template' in config['sort']:
                index_template = config['sort']['series_index_template']

        
    except Exception as err:
        print('[red]Config error:[/]')
        print(err)