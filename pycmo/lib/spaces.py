from gymnasium import spaces
import numpy as np

from pycmo.lib.features import Mount, Loadout

# CONSTANTS
pycmo_text_max_length = 2000
pycmo_max_int = 2 ** 62
pycmo_max_float = float(2 ** 62)
text_charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ~`!@#$%^&*()-_=+[]{{}}\\|;:'\",./<>?"

def get_weapon_space() -> spaces.Dict:
    weapon_space = spaces.Dict(
        {
            "ID": spaces.Text(max_length=pycmo_text_max_length, charset=text_charset),
            "WeaponID": spaces.Box(0, pycmo_max_int, dtype=np.int64),
            "QuantRemaining": spaces.Box(0, pycmo_max_int, dtype=np.int64),
            "MaxQuant": spaces.Box(0, pycmo_max_int, dtype=np.int64),
        }
    )
    return weapon_space

def get_contact_space() -> spaces.Dict:
    contact_space = spaces.Dict(
        {
            "ID": spaces.Text(max_length=pycmo_text_max_length, charset=text_charset),
            "Name": spaces.Text(max_length=pycmo_text_max_length, charset=text_charset),
            "CS": spaces.Box(0.0, pycmo_max_float, dtype=np.float64),
            "CA": spaces.Box(-pycmo_max_float, pycmo_max_float, dtype=np.float64),
            "Lon": spaces.Box(-180.0, 180.0, dtype=np.float64),
            "Lat": spaces.Box(-90.0, 90.0, dtype=np.float64),
        }
    )
    return contact_space

def get_mount_space(num_weapons:int=0) -> spaces.Dict:
    mount_dict =  {
        "ID": spaces.Text(max_length=pycmo_text_max_length, charset=text_charset),
        "Name": spaces.Text(max_length=pycmo_text_max_length, charset=text_charset),
        "DBID": spaces.Box(0, pycmo_max_int, dtype=np.int64),
    }
    if num_weapons > 0:
        mount_dict["Weapons"] = spaces.Tuple([get_weapon_space() for _ in range(num_weapons)])
    mount_space = spaces.Dict(mount_dict)
    return mount_space

def get_loadout_space(num_weapons:int=0) -> spaces.Dict:
    loadout_dict =  {
        "ID": spaces.Box(0, pycmo_max_int, dtype=np.int64),
        "Name": spaces.Text(max_length=pycmo_text_max_length, charset=text_charset),
        "DBID": spaces.Box(0, pycmo_max_int, dtype=np.int64),
    }
    if num_weapons > 0:
        loadout_dict["Weapons"] = spaces.Tuple([get_weapon_space() for _ in range(num_weapons)])
    loadout_space = spaces.Dict(loadout_dict)
    return loadout_space

def get_unit_space() -> spaces.Dict:
    unit_dict = spaces.Dict(
        {
            "ID": spaces.Text(max_length=pycmo_text_max_length, charset=text_charset),
            "Name": spaces.Text(max_length=pycmo_text_max_length, charset=text_charset),
            "Side": spaces.Text(max_length=pycmo_text_max_length, charset=text_charset),
            "Type": spaces.Text(max_length=pycmo_text_max_length),
            "CH": spaces.Box(0.0, 360.0, dtype=np.float64),
            "CS": spaces.Box(0.0, pycmo_max_float, dtype=np.float64),
            "CA": spaces.Box(-pycmo_max_float, pycmo_max_float, dtype=np.float64),
            "Lon": spaces.Box(-180.0, 180.0, dtype=np.float64),
            "Lat": spaces.Box(-90.0, 90.0, dtype=np.float64),
            "CurrentFuel": spaces.Box(0.0, pycmo_max_float, dtype=np.float64),
            "MaxFuel": spaces.Box(0.0, pycmo_max_float, dtype=np.float64),
        }
    )
    unit_space = spaces.Dict(unit_dict)
    return unit_space

def add_mount_space_to_unit_space(unit_space:spaces.Dict, mounts:list[Mount]) -> spaces.Dict:
    if len(mounts) > 0:
        mounts_dict = {}
        for mount in mounts:
            mounts_dict[str(mount.ID)] = get_mount_space(num_weapons=len(mount.Weapons))
        unit_space["Mounts"] = spaces.Dict(mounts_dict)
    return unit_space

def add_loadout_space_to_unit_space(unit_space:spaces.Dict, loadout:Loadout) -> spaces.Dict:
    unit_space["Loadout"] = get_loadout_space(num_weapons=len(loadout.Weapons))
    return unit_space
