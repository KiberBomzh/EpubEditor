import tomllib
from pathlib import Path

from epubeditor.cli import args


config_path = '.config/epubeditor/config.toml'
config_file = Path.home() / config_path
if config_file.exists() and not args.ignore_config:
    try:
        with open(config_file, 'rb') as f:
            config = tomllib.load(f)
    except Exception as err:
        print('Config error:')
        print(err)
        config = []
else:
    config = []