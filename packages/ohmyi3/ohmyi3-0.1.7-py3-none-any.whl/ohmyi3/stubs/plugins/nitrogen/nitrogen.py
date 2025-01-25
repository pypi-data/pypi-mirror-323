import uvicore
from uvicore.support.dumper import dump, dd
from ohmyi3.util import path, exists, shell

class Nitrogen:
    """
    Ohmyi3 Nitrogen Wallpaper Plugin
    Copyright (c) 2023 Matthew Reschke License http://mreschke.com/license/mit
    """

    def __init__(self, config):
        """Instantiate Plugin with User Configuration"""
        self.config = config

    def set_wallpaper(self):
        """Set nitrogen wallpaper based on selected theme"""
        theme = self.config.theme
        themes = self.config.themes
        themes_path = self.config.paths.ohmyi3_themes
        wallpaper_base = self.config.wallpaper_base

        # Get theme background file (jpg or png)
        background = None
        theme_path = path([self.config.paths.ohmyi3_themes, self.config.theme])
        jpg = path([theme_path, 'background.jpg'])
        png = path([theme_path, 'background.jpg'])
        if exists(jpg): background = jpg
        if exists(png): background = png

        # Check for background override
        override = themes.dotget(f"{theme}.wallpaper")
        if override: background = path(f"{wallpaper_base}/{override}")

        # If no theme background file or override found, don't set background
        if not background: return

        # If background found, set it using nitrogen
        if exists(background):
            cmd = f"nitrogen --save --set-zoom-fill {background} > /dev/null 2>&1"
            #cmd = f"nitrogen --save --set-scaled {background} > /dev/null 2>&1"
            uvicore.log.item4(f"Plugin Nitrogen: {cmd}")
            shell(cmd)
