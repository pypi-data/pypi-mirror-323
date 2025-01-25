import uvicore
from uvicore.console.package.registers import Cli
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd


@uvicore.provider()
class Ohmyi3(Provider, Cli):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # Register configs
        # If config key already exists items will be deep merged allowing
        # you to override granular aspects of other package configs
        self.configs([
            # Here self.name is your packages name (ie: ohmyi3).
            {'key': self.name, 'module': 'ohmyi3.config.package.config'},
        ])

    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted, self.booted')"""

        # Define Service Provider Registrations
        self.registers(self.package.config.registers)

        # Define CLI commands to be added to the ./uvicore command line interface
        self.register_commands()

    def register_commands(self) -> None:
        """Register CLI commands to be added to the ./uvicore command line interface"""

        # Or you can define commands as kwargs (multiple calls to self.commands() are appended)
        self.register_cli_commands(
            group='i3ctl',
            help='Ohmyi3 i3ctl Commands and Setuptools Entrypoint',
            commands={
                'generate': 'ohmyi3.commands.generate.cli',
                'gen': 'ohmyi3.commands.generate.cli',
                'g': 'ohmyi3.commands.generate.cli',
                'init': 'ohmyi3.commands.init.cli',
                'info': 'ohmyi3.commands.info.cli',
                'i': 'ohmyi3.commands.info.cli',
            },
        )
