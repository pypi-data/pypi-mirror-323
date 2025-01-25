import shutil
import uvicore
from uvicore.support.dumper import dump, dd
from ohmyi3.util import path, exists, shell, template

class Polybar:
    """
    Ohmyi3 Polybar Plugin
    Copyright (c) 2023 Matthew Reschke License http://mreschke.com/license/mit
    """

    def __init__(self, config):
        """Instantiate Plugin with User Configuration"""
        self.config = config

    def adjust_polybar(self):
        # Get polybar config
        polybar = self.config.polybar

        # If polybar not enabled, skip
        if not polybar.enabled: return

        # Polybar base path
        base = self.config.paths.polybar

        # Main running polybar config for this theme
        # Because the style switcher COPIES the config.ini into this main running ini
        running_ini = path([base, polybar.theme, 'config.ini'])

        # Get the themes panel folder
        panel_folder = path([base, polybar.theme, 'panel'])

        # Get the themes ini and template
        config_ini = path([panel_folder, polybar.subtheme + '.ini'])
        config_j2_ini = path([panel_folder, polybar.subtheme + '.j2.ini'])

        # Get the shared modules ini and template
        modules_ini = path([base, polybar.theme, 'modules.ini'])
        modules_j2_ini = path([base, polybar.theme, 'modules.j2.ini'])

        # Get the shared bars ini and template
        bars_ini = path([base, polybar.theme, 'bars.ini'])
        bars_j2_ini = path([base, polybar.theme, 'bars.j2.ini'])

        # Log output
        uvicore.log.item4(f'Plugin Polybar: Templating {config_j2_ini}')

        # Validation of .j2 file
        if not exists(config_j2_ini):
            uvicore.log.error(f'Cannot find {config_j2_ini}')
            return

        # Write config.ini from config.j2.ini
        template(config_j2_ini, output=config_ini, values=self.config)

        # Write modules.ini from modules.j2.ini
        template(modules_j2_ini, output=modules_ini, values=self.config)

        # Write bars.ini from bars.j2.ini
        template(bars_j2_ini, output=bars_ini, values=self.config)

        # Copy this templated config.ini to the main running_ini
        shutil.copy(config_ini, running_ini)
