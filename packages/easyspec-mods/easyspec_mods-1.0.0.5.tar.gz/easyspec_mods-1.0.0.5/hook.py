import importlib
import json
import os
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from pathlib import Path
import sys
import toml

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        # Code in this function will run before building

        # Read the pyproject.toml file
        pyproject_path = os.path.join(self.root, 'pyproject.toml')
        with open(pyproject_path, 'r', encoding='utf-8') as pyproject_file:
            pyproject_data = toml.load(pyproject_file)
        
        # Extract the [tool.modules] section
        # You can change 'modules' to whatever section name you use
        modules_data = pyproject_data.get('tool', {}).get('modules', {})
        
        if not modules_data:
            print("No modules found in pyproject.toml")
            return
        
        # Map to store the module names and paths
        modules_map = {}
        
        for module_name, module_info in modules_data.items():
            modules_map[module_name] = module_info
        
        # Create the JSON file with the module map
        json_file_path = os.path.join(self.root, 'src', 'package_map.json')
        
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(modules_map, json_file, indent=4)

        sys.stdout.write(f"Module map created: {json_file_path}")