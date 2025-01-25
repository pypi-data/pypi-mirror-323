import os
import sys
import uvicore
from uvicore.console import group
from ohmyi3.package import bootstrap
from uvicore.support.module import load

# Bootstrap the Uvicore application from the console entrypoint
app = bootstrap.Application(is_console=True)()

# Define a new asyncclick group
@group()
def cli():
    """Ohmyi3 - The dynamic variable driven i3 configuration manager

    Copyright (c) 2023 Matthew Reschke License http://mreschke.com/license/mit
    """
    pass

# Dynamically add in all commands from this package matching this command_group
command_group='i3ctl'
package = uvicore.app.package(main=True);
if ('console' in package and package.registers.commands and uvicore.app.is_console):
    for key, group in package.console['groups'].items():
        if key == command_group:
            for command_name, command_class in group.commands.items():
                cli.add_command(load(command_class).object, command_name)

# Instantiate the asyncclick group
try:
    cli(_anyio_backend='asyncio')
except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
