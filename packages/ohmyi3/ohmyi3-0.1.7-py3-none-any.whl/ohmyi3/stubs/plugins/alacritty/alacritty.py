import uvicore
from uvicore.support.dumper import dump, dd
from ohmyi3.util import path, exists, template

class Alacritty:
    """
    Ohmyi3 Alacritty Terminal Plugin
    Copyright (c) 2023 Matthew Reschke License http://mreschke.com/license/mit
    """

    def __init__(self, config):
        """Instantiate Plugin with User Configuration"""
        self.config = config

    def template_config(self):
        """Template the alacritty.yml config"""
        base = self.config.paths.alacritty
        j2_yml = path([base, 'alacritty.j2.yml'])
        yml = path([base, 'alacritty.yml'])

        # Log output
        uvicore.log.item4(f'Plugin Alacritty: Templating {j2_yml}')

        # Validation
        if not exists(j2_yml):
            uvicore.log.error(f'Cannot find {j2_yml}')
            return

        # Write template
        template(j2_yml, output=yml, values=self.config)

