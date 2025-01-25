import os
import sys
import shutil
import uvicore
from glob import glob
from uvicore.typing import Dict
from ohmyi3.util import path, now, template
from uvicore.support.dumper import dump, dd
from uvicore.exceptions import SmartException

from uvicore.console import command, argument, option


from ohmyi3 import i3ctl


@command()
async def cli():
    """Dynamically Generate a new i3 config using Ohmyi3"""

    # Get the user config files
    userconfig = i3ctl.import_userconfig()

    # Get the actual user config Superdict
    config = userconfig.config()

    # Get ohmyi3 paths
    ohmyi3_path = uvicore.config('ohmyi3.config_path')
    ohmyi3_configd_path = config.paths.ohmyi3_configd
    ohmyi3_themes_path = config.paths.ohmyi3_themes

    # Start the generation
    uvicore.log.header("Generating new i3 config using ohmyi3")

    # Fire off user defined before_generate_hook
    uvicore.log.item3("Firing user defined before_generate hook")
    await userconfig.before_generate(config)

    # If i3 config exists, back it up
    i3config_file = f"{config.paths.i3}/config"
    if os.path.exists(i3config_file):
        backup = path([config.paths.i3, 'backup-' + now()])
        uvicore.log.item(f"Backing up {i3config_file} to {backup}")
        shutil.copy(i3config_file, backup)

    # Get all config.d/* files
    files = sorted(glob(ohmyi3_configd_path + "/*.conf"))

    # Get active theme path
    active_theme_path = f"{ohmyi3_themes_path}/{config.theme}"

    # Append config.d/* and theme.d/theme to new i3 config
    with open(i3config_file, "w") as f:
        # Loop and merge each config and append to
        for file in files:
            uvicore.log.item2(f"Appending {file}")
            f.write(template(file, values=config))
            f.write("\n\n\n\n\n")

        # Append the selected theme files
        theme_file = path([active_theme_path, 'theme.conf'])
        if os.path.exists(theme_file):
            uvicore.log.item(f"Appending THEME {config.theme}")
            f.write(template(theme_file, values=config))

    # Copy themed i3status or a default if no theme specific file exists
    i3status_template_path = None
    if os.path.exists(f"{active_theme_path}/i3status.conf"):
        # Use themed i3status.conf
        i3status_template_path = active_theme_path
    elif os.path.exists(f"{ohmyi3_themes_path}/i3status.conf"):
        # Use default i3status.conf
        i3status_template_path = f"{ohmyi3_themes_path}"

    if i3status_template_path:
        uvicore.log.item(f"Copying {i3status_template_path}/i3status.conf to {config.paths.i3status}/config")
        with open(f"{config.paths.i3status}/config", "w") as f:
            f.write(template('i3status.conf', base=i3status_template_path, values=config))

    # Fire off user defined afer_generate_hook
    uvicore.log.item3("Firing user defined after_generate hook")
    await userconfig.after_generate(config)

    # Cleanup __pycache__
    pycache = path([ohmyi3_path, '__pycache__'])
    if os.path.exists(pycache):
        shutil.rmtree(pycache)

    # Done
    uvicore.log.nl()
    uvicore.log("Done!")
    uvicore.log(f"New {i3config_file} generated!")
    uvicore.log("Please reload i3!")
