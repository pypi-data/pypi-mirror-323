import os
import platform
import subprocess
from uvicore.typing import Dict
from datetime import datetime
from uvicore.support.module import load
from jinja2 import Environment as JinjaEnv
from uvicore.support.dumper import dump, dd
from jinja2 import FileSystemLoader as JinjaLoader

def plugin(module, **kwargs):
    return load('plugins.' + module).object


def path(location, must_exist=False, notfound_message=None):
    """Path helper with realpath and expanduser capabilities"""
    if type(location) == list:
        # If location is a list, join together with /
        location = "/".join(location)

    # Get real expanded path
    real = os.path.realpath(os.path.expanduser(location))

    # If must_exist, ensure it exists or display a message and exit
    if must_exist:
        if not os.path.exists(real):
            print(f"{real} not found")
            if notfound_message: print(notfound_message)
            exit(1)

    # Return real expanded path
    return real


def exists(location):
    """Check if path exists, using path() helper for realpath and expanduser"""
    return os.path.exists(path(location))


def now(dateformat='%Y-%m-%d_%H-%M-%S'):
    """Get now() date time in specified format (defaults 2021-01-24_19-24-58)"""
    return datetime.now().strftime(dateformat)


def shell(cmd):
    """Execute a shell command"""
    #return os.system(cmd)
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8').split()


def template(file, *, base=None, output=None, values=None) -> str:
    """Render a single file through the Jinja2 templating system, return or write output"""
    if not base: base = os.path.dirname(file)
    base = path(base)
    filename = os.path.basename(file)
    loader = JinjaLoader(searchpath=base)
    env = JinjaEnv(loader=loader)
    template = env.get_template(filename)
    rendered = template.render(values)
    if output:
        with open(output, 'w') as f:
            f.write(rendered)
    return rendered


def loggedinuser():
    try:
        username = os.getlogin()
    except:
        uid = os.getuid()
        import pwd
        username = pwd.getpwuid(uid).pw_name
    return username


def hostname():
    return platform.node()


def gather(locals):
    """Gather variables that do not begin with _ or 'set' as a Superdict"""
    _variables = Dict()
    ignore_keys = ['_', 'set', 'gather', 'Dict', 'path', 'plugin', 'dump', 'dd', 'env', 'util', 'uvicore']
    for key, value in locals.items():
        if key[0] not in ignore_keys and key not in ignore_keys:
            _variables[key] = value
    return _variables


def set(default, *args):
    """Return the default value plus deep merged overrides based on infinite conditions"""
    # Convert infinite args into a list[tuple]
    # Where each tuple in the list is a Boolean, and the value to use
    #dd(args)
    it = iter(args)
    conditions = [*zip(it, it)]

    # If the default is a dict, convert to Superdict
    if type(default) == dict: default = Dict(default)

    # Loop all (condition,value) tuples
    for condition in conditions:

        # Compare is either a boolean or a value to match the override Dict to
        compare = condition[0]

        # Ger our override value from the tuple
        override = condition[1]

        # If override is a dict, convert to Superdict
        if type(override) == dict: override = Dict(override)

        # Condition is a bool True or False
        if type(compare) == bool:
            # If conditoin is False, ignore this override
            if condition[0] == False: continue

            # Merge or overwrite the values
            if type(default) == Dict and type(override) == Dict:
                # Deep merge the override into the default
                for k, v in override.items():
                    default.dotset(k, v)
            else:
                default = override
        else:
            # Condition is a value, and the override is a Dict of overrides IF the value matches
            for key, value in override.items():
                if key == compare:
                    if type(default) == Dict and type(override) == Dict:
                        # Deep merge the override into the default
                        for k, v in value.items():
                            default.dotset(k, v)
                    else:
                        default = value

    # Finally, return deep merged default with all matching overrides
    return default






# class Overridable:
#     """Store all locals() for further set() overridable commands"""

#     def __init__(self, **kwargs):
#         self.kwargs = kwargs

#     def __call__(self, default, **kwargs):
#         # If type of default is dict, convert to Superdict
#         if type(default) == dict: default = Dict(default)

#         # Loop each possible if_* override kwargs
#         for override_key, override_value in kwargs.items():
#             override_key = override_key[3:]

#             # If type of override_value is dict, convert to Superdict
#             if type(override_value) == dict: override_value = Dict(override_value)

#             # If the override_key is found in our Overridable values
#             if override_key in self.kwargs:
#                 # Get the override_keys value
#                 override_key_value = self.kwargs[override_key]

#                 # Loop our the passed in override_value for matching override_key_value
#                 for k, v in override_value.items():
#                     if k == override_key_value:
#                         if type(default) == Dict:
#                             for findkey, newvalue in v.items():
#                                 #default.dotset(findkey, newvalue)
#                                 default.dotset(findkey, newvalue)
#                                 #v = default
#                                 #dd(v)
#                             #return default
#                         else:
#                             default = v
#         return default
