import uvicore
from uvicore.support.dumper import dump, dd
from uvicore.exceptions import SmartException
from uvicore.console import command, argument, option

from ohmyi3 import i3ctl

@command()
async def cli():
    """Display ohmyi3 configuration information"""

    # Get the user config
    config = i3ctl.import_userconfig().config()

    uvicore.log.header("Ohmyi3 User Configuration")
    uvicore.log.nl()
    dump(config)

