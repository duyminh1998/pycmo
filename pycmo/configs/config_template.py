# Author: Minh Hua
# Date: 08/22/2021
# Purpose: Edit the paths in the get_config function as needed and rename this file to config.py.

import os

def get_config():
    pycmo_path = os.path.join("path/to", "pycmo")
    cmo_path = os.path.join("path/to/steam/installation/of", "Command - Modern Operations")

    return {
    "command_path": cmo_path,
    "pycmo_path": pycmo_path,
    "observation_path": os.path.join(pycmo_path, "xml", "steps"),
    "steam_observation_folder_path": os.path.join(cmo_path, 'ImportExport'),
    "scen_ended": os.path.join(pycmo_path, "pycmo", "configs", "scen_has_ended.txt"),
    "pickle_path": os.path.join(pycmo_path, "pickle"),
    "scripts_path": os.path.join(pycmo_path, "scripts"),
    "command_mo_version": "Command v1.06 - Build 1328.11"
    # "command_cli_output_path": "C:\\ProgramData\\Command Professional Edition 2\\Analysis_Int", # only applicable to Premium version so we update this later
    }