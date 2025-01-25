import os
import shutil
import uvicore
from ohmyi3 import i3ctl
from ohmyi3.util import path
from uvicore.support.dumper import dump, dd
from uvicore.exceptions import SmartException
from uvicore.console import command, argument, option

@command()
async def cli():
    """Initialize a stock ~/.config/ohmyi3/* configuration"""

    # Get the user config
    config_path = path(uvicore.config('ohmyi3.config_path'))
    app_path = path(uvicore.app.package(main=True).path, True)
    stubs_path = path([app_path, 'stubs'], True)

    uvicore.log.header(f'Initializing ohmyi3 to {config_path}')

    # Create ~/.config/ohmyi3/ and copy stubs
    if not os.path.exists(config_path):
        uvicore.log.item(f"Creating {config_path} folder")
        uvicore.log.item(f"Copying base configs into {config_path} folder")
        shutil.copytree(stubs_path, config_path)

    # Get the user config
    config = i3ctl.import_userconfig().config()

    # Get i3 and i3status path
    i3_path = config.paths.i3 if config.paths.i3 else path('~/.config/i3')
    i3status_path = config.paths.i3status if config.paths.i3status else path('~/.config/i3status')

    # Create ~/.config/i3
    if not os.path.exists(i3_path):
        uvicore.log.item(f"Creating {i3_path} folder")
        os.mkdir(i3_path)

    # Create ~/.config/i3status
    if not os.path.exists(i3status_path):
        uvicore.log.item(f"Creating {i3status_path} folder")
        os.mkdir(i3status_path)

    uvicore.log.nl()
    uvicore.log('Done!  Now run: i3ctl generate')
