import uvicore
from ohmyi3 import util
from uvicore.support.dumper import dump, dd

class Archey3:
    """
    Ohmyi3 Archey3 Plugin
    Copyright (c) 2023 Matthew Reschke License http://mreschke.com/license/mit
    """

    def __init__(self, config):
        """Instantiate Plugin with User Configuration"""
        self.config = config

    def set_archey(self):
        """Set ~/.zshrc archey3 color based on theme"""
        themes = self.config.themes
        theme = self.config.theme
        color = themes.dotget(f"{theme}.archey3")

        if not color: return
        if util.exists('~/.zshrc'):
            cmd = f"sed -i 's/archey3.*/archey3 -c {color}/g' ~/.zshrc"
            uvicore.log.item4(f"Plugin Archey3: {cmd}")
            util.shell(cmd)
        if util.exists('~/.bashrc'):
            cmd = f"sed -i 's/archey3.*/archey3 -c {color}/g' ~/.bashrc"
            uvicore.log.item4(f"Plugin Archey3: {cmd}")
            util.shell(cmd)
