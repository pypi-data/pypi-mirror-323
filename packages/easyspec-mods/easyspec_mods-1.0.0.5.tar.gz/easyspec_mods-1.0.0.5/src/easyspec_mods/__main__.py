import code
import json
import os
from easyspec_mods.utils import *
try:
    import IPython
    ipython_available = True
except ImportError:
    ipython_available = False

package_map = {}

def main_cli():

    # Print header with main package metadata
    print_beautiful_header(__package__)

    # Menu with available modules
    package_map_path = os.path.join(os.path.dirname(__file__), 'package_map.json')
    with open(package_map_path, 'r') as f:
        global package_map
        package_map = json.load(f)
    display_package_menu(package_map)
    module_selection(globals())

    if ipython_available:
        # Start IPython shell quietly if available
        IPython.start_ipython(argv=[], exit_code=0, user_ns=globals(), display_banner=False)
    else:
        # Fall back to regular Python shell
        code.interact(banner='', local=globals())

def modules():
    cls()
    display_package_menu(package_map)
    module_selection(globals())