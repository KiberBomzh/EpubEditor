import tomllib
from pathlib import Path
from os import getenv

from epubeditor.cli import args


HOME = getenv('HOME', str(Path.home())) + '/.config'
config_home = getenv('XDG_CONFIG_HOME', HOME)

config_path = 'epubeditor/config.toml'
config_file = Path(config_home) / config_path

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