# Author: Minh Hua
# Date: 08/16/2021
# Purpose: Export Command raw data into Features object and flatten into agent-consummable data.

# imports
import xml.etree.ElementTree as ET
import xmltodict
import collections

# Game 
Game = collections.namedtuple("Game", ["TimelineID", "Time", "ScenarioName", "ZeroHour", "StartTime", "Duration", "Sides"])
# Side 
Side = collections.namedtuple("Side", ['ID', 'Name', 'TotalScore'])
# Unit 
Unit = collections.namedtuple("Unit", ['XML_ID', 'ID', 'Name', 'Side', 'DBID', 'Type',
                                        'CH', 'CS', 'CA', 'Lon', 'Lat', 'Mounts', 'Loadout'])
# add fuel
# Mount 
Mount = collections.namedtuple("Mount", ["XML_ID", "ID", "Name", "Side", "DBID", "Weapons"])
# Loadout
Loadout = collections.namedtuple("Loadout", ["XML_ID", "ID", "Name", "Side", "DBID", "Weapons"])
# Weapon
Weapon = collections.namedtuple("Weapon", ["XML_ID", "ID", "Side", "WeaponID", "QuantRemaining"])
# Contacts 
Contact = collections.namedtuple("ContactInfo", ["XML_ID", "ID", 'CS', 'CA', 'Lon', 'Lat'])

def features_from_game_(xml, side):
    """Construct a Features object using data extracted from game."""
    features = Features(xml, side)
    return features

class Features(object):    
    def __init__(self, xml: str, player_side: str):
        """Render feature layers from Command scenario XML into named tuples.
        Args:
            xml:
            player_side:
        """
        try:
            tree = ET.parse(xml) # This variable contains the XML tree
            root = tree.getroot() # This is the root of the XML tree
            xmlstr = ET.tostring(root)            
            self.scen_dic = xmltodict.parse(xmlstr) # our scenario xml is now in 'dic'
        except FileNotFoundError as error:
            print("ERROR: Unable to parse scenario xml.")
            raise
        self.player_side = player_side
        self.meta = self.get_meta() # Return the scenario-level rmation of the scenario
        self.units = self.get_side_units(player_side)
        player_side_index = self.get_sides().index(player_side)
        self.side_ = self.get_side_properties(player_side_index)
        self.contacts = self.get_contacts(player_side_index)
        
    def transform_obs_into_arrays(self):
        """Render some Command observations into something an agent can handle."""
        observation = [self.meta, self.units, self.side_, self.contacts]
        return observation

    # XML Data Extraction Methods
    def get_meta(self) -> Game:
        """Get meta data (top-level scenario data)"""
        try:
            return Game(self.scen_dic['Scenario']["TimelineID"],
                            self.scen_dic['Scenario']["Time"],
                            self.scen_dic['Scenario']["Title"],
                            self.scen_dic['Scenario']["ZeroHour"],
                            self.scen_dic['Scenario']["StartTime"],
                            self.scen_dic['Scenario']["Duration"],
                            self.get_sides())
        except KeyError:
            print("ERROR: failed to get scenario properties.")
            raise

    def get_sides(self) -> list:
        """Get the number and names of all sides in a scenario"""
        try:
            return [self.scen_dic['Scenario']['Sides']['Side'][i]['Name'] for i in range(len(self.scen_dic['Scenario']['Sides']['Side']))]
        except KeyError:
            print("ERROR: failed to get list of side names in scenario.")
            raise

    def get_side_properties(self, side_id = 0) -> Side:
        """Get the properties (score, name, etc.) of a side"""
        try:
            return Side(self.scen_dic['Scenario']['Sides']['Side'][side_id]['ID'],
                            self.scen_dic['Scenario']['Sides']['Side'][side_id]['Name'],
                            self.scen_dic['Scenario']['Sides']['Side'][side_id]['TotalScore'])
        except KeyError:
            print("ERROR: failed to get side properties.")
            raise

    def get_side_units(self, side_id_str=None) -> list:
        """Get all the units of a side"""
        unit_ids = []
        if side_id_str == None or 'ActiveUnits' not in self.scen_dic["Scenario"].keys():
            return unit_ids
        for key in self.scen_dic["Scenario"]["ActiveUnits"].keys():
            active_units = self.scen_dic["Scenario"]["ActiveUnits"][key]
            if not isinstance(self.scen_dic["Scenario"]["ActiveUnits"][key], list):
                active_units = [self.scen_dic["Scenario"]["ActiveUnits"][key]]
            for i in range(len(active_units)):
                if active_units[i]["Side"] == side_id_str:
                    unit_id = active_units[i]['ID']
                    name = active_units[i]['Name']
                    dbid = active_units[i]['DBID']
                    lon = active_units[i]['LonLR']
                    lat = active_units[i]['LatLR']
                    ch = None
                    cs = None
                    ca = None
                    loadout = None
                    mount = None
                    if 'Loadout' in active_units[i].keys() and active_units[i]['Loadout'] != None:
                        loadout = self.get_loadout(key, i)
                    if 'Mounts' in active_units[i].keys() and active_units[i]['Mounts'] != None:
                        mount = self.get_mount(key, i)
                    if 'CH' in active_units[i].keys() and active_units[i]['CH'] != None:
                        ch = active_units[i]['CH']
                    if 'CS' in active_units[i].keys() and active_units[i]['CS'] != None:
                        cs = active_units[i]['CS']
                    if 'CA' in active_units[i].keys() and active_units[i]['CA'] != None:
                        ca = active_units[i]['CA']
                    unit_ids.append(Unit(i, unit_id, name, self.player_side, dbid, key, ch, cs, ca, lon, lat, mount, loadout))
        return unit_ids

    def get_mount(self, unit_type, unit_xml_id=None):
        mounts = []
        if unit_xml_id != None:
            mount = self.scen_dic["Scenario"]["ActiveUnits"][unit_type][unit_xml_id]["Mounts"]["Mount"]
        else:
            mount = self.scen_dic["Scenario"]["ActiveUnits"][unit_type]["Mounts"]["Mount"]
        if isinstance(mount, list): 
            for i in range(len(mount)):
                id = mount[i]["ID"]
                name = mount[i]["Name"]
                dbid = mount[i]["DBID"]
                mounts.append(Mount(i, id, name, self.player_side, dbid, self.get_weapon('Mount', unit_type, unit_xml_id, i)))
        else:
            id = mount["ID"]
            name = mount["Name"]
            dbid = mount["DBID"]
            mounts.append(Mount(0, id, name, self.player_side, dbid, self.get_weapon('Mount', unit_type, unit_xml_id)))
        return mounts      

    def get_loadout(self, unit_type, unit_xml_id=None):
        if unit_xml_id != None:
            loadout = self.scen_dic["Scenario"]["ActiveUnits"][unit_type][unit_xml_id]["Loadout"]["Loadout"]
        else:
            loadout = self.scen_dic["Scenario"]["ActiveUnits"][unit_type]["Loadout"]["Loadout"]
        id = loadout["ID"]
        name = loadout["Name"]
        dbid = loadout["DBID"]
        return Loadout(0, id, name, self.player_side, dbid, self.get_weapon('Loadout', unit_type, unit_xml_id))
    
    def get_weapon(self, mount_or_loadout, unit_type, unit_xml_id=None, mount_id=None):
        weapons = []
        if mount_or_loadout == "Loadout":
            if unit_xml_id != None:
                loadout = self.scen_dic["Scenario"]["ActiveUnits"][unit_type][unit_xml_id]["Loadout"]["Loadout"]
            else:
                loadout = self.scen_dic["Scenario"]["ActiveUnits"][unit_type]["Loadout"]["Loadout"]
            if loadout['Weaps'] == None:
                return weapons
            wrec = loadout['Weaps']['WRec']
            for i in range(len(wrec)):
                try:
                    weapons.append(Weapon(i, wrec[i]["ID"], self.player_side, wrec[i]['WeapID'], wrec[i]["CL"]))
                except KeyError:
                    weapons.append(Weapon(0, wrec["ID"], self.player_side, wrec['WeapID'], wrec["CL"]))
            return weapons
        elif mount_or_loadout == "Mount":
            if mount_id == None:
                if unit_xml_id != None:
                    mount = self.scen_dic["Scenario"]["ActiveUnits"][unit_type][unit_xml_id]["Mounts"]["Mount"]
                else:
                    mount = self.scen_dic["Scenario"]["ActiveUnits"][unit_type]["Mounts"]["Mount"]
            else:
                if unit_xml_id != None:
                    mount = self.scen_dic["Scenario"]["ActiveUnits"][unit_type][unit_xml_id]["Mounts"]["Mount"][mount_id]
                else:
                    mount = self.scen_dic["Scenario"]["ActiveUnits"][unit_type]["Mounts"]["Mount"][mount_id]
            if mount['MW'] == None:
                return weapons
            wrec = mount['MW']['WRec']
            for i in range(len(wrec)):
                if isinstance(wrec, list):
                    try:
                        weapons.append(Weapon(i, wrec[i]["ID"], self.player_side, wrec[i]['WeapID'], wrec[i]["CL"]))
                    except:
                        pass
                else:
                    try:
                        weapons.append(Weapon(0, wrec["ID"], self.player_side, wrec['WeapID'], wrec["CL"]))
                    except:
                        pass
            return weapons

    def get_contacts(self, side_id = 0) -> list:
        """Return the contacts of a side"""
        try:
            contact_id = []
            if "Contacts" in self.scen_dic["Scenario"]["Sides"]["Side"][side_id].keys():
                contacts = self.scen_dic["Scenario"]["Sides"]["Side"][side_id]["Contacts"]["Contact"]
                if not isinstance(contacts, list):
                    contacts = [self.scen_dic["Scenario"]["Sides"]["Side"][side_id]["Contacts"]["Contact"]]
                for i in range(len(contacts)):
                    cs = None
                    ca = None
                    lon = None
                    lat = None
                    if 'CS' in contacts[i].keys() and contacts[i]['CS'] != None:
                        cs = contacts[i]['CS']
                    if 'CA' in contacts[i].keys() and contacts[i]['CA'] != None:
                        ca = contacts[i]['CA']
                    if 'Lon' in contacts[i].keys() and contacts[i]['Lon'] != None:
                        lon = contacts[i]['Lon']
                    if 'Lat' in contacts[i].keys() and contacts[i]['Lat'] != None:
                        lat = contacts[i]['Lat']                        
                    contact_id.append(Contact(i, contacts[i]["ID"], cs, ca, lon, lat))
                return contact_id
            else:
                return contact_id
        except KeyError:
            print("KeyError: failed to get side contacts.")
            return contact_id
        except:
            print("ERROR: failed to get side contacts.")
            return contact_id

# tests
if __name__ == '__main__':
    features = features_from_game_("C:\\Users\\minhh\\Documents\\MyProjects\\pycmo\\raw\\wooden_leg_w_contacts.xml", "Israel")
    print(features.units['Aircraft'][0]['Lat'])
    pass
