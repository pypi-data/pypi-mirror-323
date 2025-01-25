import os
import sys
import uvicore
from ohmyi3.util import path


def import_userconfig():
    """Dynamically import the users ~/.config/ohmyi3/configurator.py"""

    config_folder = path(uvicore.config('ohmyi3.config_path'), True,
        notfound_message="Perhpas you havent run 'i3ctl init' yet??")

    # App userconfig path to sys.path for imports
    sys.path.append(os.path.realpath(config_folder))
    import config
    return config


