import builtins
from easyspec_mods.utils import CleanExit

# Override the standard exit() function
# Make it work also within IPython
builtins.exit = CleanExit()

