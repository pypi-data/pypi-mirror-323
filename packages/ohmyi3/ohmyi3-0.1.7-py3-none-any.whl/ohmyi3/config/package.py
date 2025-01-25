from uvicore.configuration import env
from uvicore.typing import OrderedDict

# This is the main ohmyi3 config.  All items here can be overridden
# when used inside other applications.  Accessible at config('ohmyi3')

config = {

    # --------------------------------------------------------------------------
    # Package Custom Configuration
    # --------------------------------------------------------------------------
    'config_path': env('OHMYI3_PATH', '~/.config/ohmyi3'),


    # --------------------------------------------------------------------------
    # Package Information
    #
    # Most other info like name, short_name, vendor are derived automatically
    # --------------------------------------------------------------------------
    'version': '0.1.0',


    # --------------------------------------------------------------------------
    # Registration Control
    # --------------------------------------------------------------------------
    # This lets you control the service provider registrations.  If this app
    # is used as a package inside another app you might not want some things
    # registered in that context.  Use config overrides in your app to change
    # registrations
    'registers': {
        'commands': True,
    },


    # --------------------------------------------------------------------------
    # Package Dependencies (Service Providers)
    #
    # Define all the packages that this package depends on.  At a minimum, only
    # the uvicore.foundation package is required.  The foundation is very
    # minimal and only depends on configuration, logging and console itself.
    # You must add other core services built into uvicore only if your package
    # requires them.  Services like uvicore.database, uvicore.orm, uvicore.auth
    # uvicore.http, etc...
    # --------------------------------------------------------------------------
    'dependencies': OrderedDict({
        # Foundation is the core of uvicore and is required as the first dependency.
        # Foundation itself relys on configuration, logging, console, cache and more.
        'uvicore.foundation': {
            'provider': 'uvicore.foundation.package.provider.Foundation',
        },
    }),

}
