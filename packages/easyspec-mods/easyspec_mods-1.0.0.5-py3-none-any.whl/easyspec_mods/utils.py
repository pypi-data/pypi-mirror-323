import importlib
from importlib.metadata import metadata
import os
import sys
import textwrap

current_dir = os.getcwd()

def print_beautiful_header(package_name):
    # Fetch metadata
    pkg_metadata = metadata(package_name)
    pkg_name = pkg_metadata.get("Name", "Unknown Package").strip().upper()
    pkg_version = pkg_metadata.get("Version", "Unknown Version").strip()
    pkg_author = pkg_metadata.get("Author", next((value for key, value in pkg_metadata.items() if key.lower() == "author-email"), "Unknown Email")).strip()
    pkg_description = pkg_metadata.get("Summary", "No Description Available").strip()
    python_version = sys.version.split(" ")[0].strip()  # Get the version of Python in use
    easyspec_commands = {
                    'new_project' : 'initializes a new project directory',
                    'working_directory' : 'working directory selection',
                    'modules' : 'module selection',
                    'procedures' : 'lists procedures for current module',
                    'cls' : 'clear interface',
                    'clear'   : 'clear interface',
                    'help' : 'extra information on commands',
                    'exit' : 'exit easySpec cli',
                    }
    
    # Console window size
    terminal_width = os.get_terminal_size().columns
    
    header_width = terminal_width

    # Function to center text with padding
    def center_text(text, width):
        return text.center(width)

    # Create a formatted header with centered text
    header = f"""
    {center_text("=" * header_width, header_width)}
    {center_text(pkg_name, header_width)}
    {center_text("=" * header_width, header_width)}
    {center_text(f"Version: {pkg_version}", header_width)}
    {center_text(f"Description: {pkg_description}", header_width)}
    {center_text(f"Author: {pkg_author}", header_width)}
    {center_text("=" * header_width, header_width)}
    {' ' * 4}Python Version: {python_version}
    {center_text("-" * header_width, header_width)}
    {' ' * 4}Working Directory: {current_dir}
    {center_text("-" * header_width, header_width)}
    """

    # Wrap the text to fit the console width
    wrapped_header = textwrap.dedent(header).strip()

    # Clear the console screen (for a cleaner output)
    print("\033[H\033[J", end="")  # ANSI escape codes to clear the screen

    # Print the header
    print(wrapped_header)
    print_commands(easyspec_commands)

def dynamic_import(global_scope):
    print(" ")
    module_name = input("   Enter the module name: ").strip()
    module_path = (__package__.strip() + '.' + module_name.strip()).strip().lower()
    imported_objects = {}

    try:
        # Dynamically import the module
        module = importlib.import_module(module_path)
        # Use the passed global scope to assign imported attributes
        for attr_name in dir(module):
            if not attr_name.startswith("_"):  # Ignore private/protected attributes
                global_scope[attr_name] = getattr(module, attr_name)
                
                # Add to the dictionary for return
                imported_objects[attr_name] = getattr(module, attr_name)
                
                # Print the attribute being imported
                # print(f"Imported: {attr_name}")

        cls()
        # print(f"All functions and variables from '{module_path}' imported successfully.")
        print_procedures(module_name, module.__version__, imported_objects)
        return imported_objects  # Return the dictionary with all imported attributes
    
    except ModuleNotFoundError:
        print(f"Error: Module '{module_path}' not found.")
    except Exception as e:
        print(f"Error importing from module '{module_path}': {e}")
        return {}

def module_selection(global_scope):
    dynamic_import(global_scope)

def print_commands(commands):

    # Console window size
    terminal_width = os.get_terminal_size().columns
    
    header_width = terminal_width

    indent = ' ' * 4
    title = "Commands:"
    # Format the command list
    formatted_keys = indent + title + '    ' + '  '.join(commands.keys())
    print(formatted_keys)
    print(f"{'-' * header_width}".center(header_width))

import os

def print_procedures(module_name, module_version, procedures):
    # Filter only functions from the dictionary
    function_procedures = {k: v for k, v in procedures.items() if callable(v)}

    terminal_width = os.get_terminal_size().columns
    indent = ' ' * 4
    title = "Procedures:\n"
    col_width = 25  # Adjust the column width as needed
    max_cols = max(1, terminal_width // col_width)  # Calculate max columns based on terminal width

    # Get function names
    procedure_names = list(function_procedures.keys())

    # Split names into rows based on available columns
    rows = [procedure_names[i:i + max_cols] for i in range(0, len(procedure_names), max_cols)]

    # Print header
    print(f"\n{indent}{module_name.upper()} MODULE {module_version}\n")
    print(f"{indent}{title}")

    # Print each row with equal spacing
    for row in rows:
        formatted_row = "".join(f"{name:<{col_width}}" for name in row)
        print(indent + formatted_row)

    print(f"\n{'-' * terminal_width}".center(terminal_width))


def display_package_menu(modules):
    print("\n Module Selection:\n")
    for idx, (module, details) in enumerate(modules.items(), start=1):
        # print(f"[{idx}] {module.capitalize()} v{details['version']}")
        print(f" ° {module.capitalize()} v{details['version']}")
        print(f"   {details['description']}\n")

class ClearScreen:
    def __call__(self):
        print_beautiful_header(__package__)

clear = ClearScreen()  # Now you can call `clear` without parentheses
cls = ClearScreen()    # Same for `cls`

# Override the exit() function in the builtins module
class CleanExit:
    def __call__(self):
        self.exit()

    def exit(self):
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear console
        sys.exit(0)



