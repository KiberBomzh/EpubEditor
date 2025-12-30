import tomllib
from pathlib import Path
import os

from rich import print


from epubeditor.cli import args


# Глобальный переменные
replacement_for_forbidden_chars = '_'
no_subdirs = False
default_path = None


# [scripts]
script_path = ''


# split_by_titles
clean_body_attributes = False


# toc_from titles
include_subtitles = False
all_h = False
only_h = False


# [open]
autosave = False


# [sort]
# sort.py
main_path = None
keep_empty_folders = False
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
            if not isinstance(replacement_for_forbidden_chars, str):
                raise TypeError("'replacement_for_forbidden_chars' must be a str!")
        
        if 'no_subdirs' in config:
            no_subdirs = config['no_subdirs']
            if not isinstance(no_subdirs, bool):
                raise TypeError("'no_subdirs' must be a bool!")
        
        if 'default_path' in config:
            default_path = config['default_path']
            if not isinstance(default_path, str):
                raise TypeError("'default_path' must be a str!")
            
            if '~/' in default_path:
                default_path = os.path.expanduser(default_path)
        
        
        if 'scripts' in config:
            if 'path' in config['scripts']:
                script_path = config['scripts']['path']
                if not isinstance(script_path, str):
                    raise TypeError("'path' must be a str!")
                
                if '~/' in script_path:
                    script_path = os.path.expanduser(script_path)
                    
            
            
            if 'split_by_titles' in config['scripts']:
                split_by_titles_flags = {}
                for flag in config['scripts']['split_by_titles']:
                    split_by_titles_flags.update(flag)
                
                if 'clean_body_attributes' in split_by_titles_flags:
                    clean_body_attributes = split_by_titles_flags['clean_body_attributes']
                    if not isinstance(clean_body_attributes, bool):
                        raise TypeError("'clean_body_attributes' must be a bool!")

            
            if 'toc_from_titles' in config['scripts']:
                toc_from_titles_flags = {}
                for flag in config['scripts']['toc_from_titles']:
                    toc_from_titles_flags.update(flag)
            
                if 'include_subtitles' in toc_from_titles_flags:
                    include_subtitles = toc_from_titles_flags['include_subtitles']
                    if not isinstance(include_subtitles, bool):
                        raise TypeError("'include_subtitles' must be a bool!")
                
                if 'all_h' in toc_from_titles_flags:
                    all_h = toc_from_titles_flags['all_h']
                    if not isinstance(all_h, bool):
                        raise TypeError("'all_h' must be a bool!")
    
                if 'only_h' in toc_from_titles_flags:
                    only_h = toc_from_titles_flags['only_h']
                    if not isinstance(only_h, bool):
                        raise TypeError("'only_h' must be a bool!")

        
        
        if 'open' in config:
            if 'autosave' in config['open']:
                autosave = config['open']['autosave']
                if not isinstance(autosave, bool):
                    raise TypeError("'autosave' must be a bool!")
        
        
        if 'sort' in config:
            if 'main_path' in config['sort']:
                main_path = config['sort']['main_path']
                if not isinstance(main_path, str):
                    raise TypeError("'main_path' must be a str!")
    
            if 'keep_empty_folders' in config['sort']:
                keep_empty_folders = config['sort']['keep_empty_folders']
                if not isinstance(keep_empty_folders, bool):
                    raise TypeError("'keep_empty_folders' must be a bool!")
            
            if 'sort_template' in config['sort']:
                sort_template = config['sort']['sort_template']
                if not isinstance(sort_template, str):
                    raise TypeError("'sort_template' must be a str!")
            
            
            if 'rename_template' in config['sort']:
                name_template = config['sort']['rename_template']
                if not isinstance(name_template, str):
                    raise TypeError("'rename_template' must be a str!")
            
            
            if 'series_index_template' in config['sort']:
                index_template = config['sort']['series_index_template']
                if not isinstance(index_template, str):
                    raise TypeError("'series_index_template' must be a str!")

        
    except Exception as err:
        print('[red]Config error:[/]')
        print(err)


if args.no_subdirs:
    no_subdirs = args.no_subdirs

# Обработка флагов для комманд
match args.command:
    case 'sort':
        if args.main_path:
            main_path = args.main_path
        
        if args.keep_empty_folders:
            keep_empty_folders = args.keep_empty_folders
        
        if args.template:
            sort_template = args.template
    
    
    case 'rename':
        if args.template:
            name_template = args.template
    
    
    case 'script':
        if args.script_name == 'split_by_titles':
            if args.clean_body_attributes:
                clean_body_attributes = args.clean_body_attributes
        
        elif args.script_name == 'toc_from_titles':
            if args.include_subtitles:
                include_subtitles = args.include_subtitles
            
            if args.all_h:
                all_h = args.all_h
            
            if args.only_h:
                only_h = args.only_h
