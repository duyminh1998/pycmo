"""Export Command raw data into numpy arrays."""

import xml.etree.ElementTree as ET
import xmltodict
import collections

# Game 
Game = collections.namedtuple("Game", ["TimelineID", "Time", "ScenarioName", "ZeroHour", "StartTime", "Duration", "Sides"])
# Side 
Side = collections.namedtuple("Side", ['ID', 'Name', 'TotalScore'])
# Unit 
Unit = collections.namedtuple("Unit", ['XML_ID', 'ID', 'Name', 'Side', 'DBID', 'Type', 'Mounts', 'Loadout'])
# Mount 
Mount = collections.namedtuple("Mount", ["XML_ID", "ID", "Name", "Side", "DBID", "Weapons"])
# Loadout
Loadout = collections.namedtuple("Loadout", ["XML_ID", "ID", "Name", "Side", "DBID", "Weapons"])
# Weapon
Weapon = collections.namedtuple("Weapon", ["XML_ID", "ID", "Side", "WeaponID", "QuantRemaining"])
# Mission 
# Msn = collections.namedtuple("Msn", [])
# Contacts 
Contact = collections.namedtuple("ContactInfo", ["XML_ID", "ID"])

def features_from_game_(xml, side):
    """Construct a Features object using data extracted from game ."""
    features = Features(xml, side)
    return features

class Features(object):
    """Render feature layers from Command scenario XML into named tuples."""
    
    def __init__(self, xml, player_side):
        tree = ET.parse(xml) # This variable contains the XML tree
        root = tree.getroot() # This is the root of the XML tree
        xmlstr = ET.tostring(root)
        self.player_side = player_side
        self.scen_dic = xmltodict.parse(xmlstr) # our scenario xml is now in 'dic'
        self.player_side = player_side

        self.meta = self.get_meta() # Return the scenario-level rmation of the scenario

        self.units = self.get_side_units(player_side)
        player_side_index = self.get_sides().index(player_side)
        self.side_ = self.get_side_properties(player_side_index)
        self.contacts = self.get_contacts(player_side_index)
        # self.contact_features = self.get_contact_features(player_side_index)
        
    def transform_obs(self, obs):
        """Render some Command observations into something an agent can handle."""
        observation = [self.meta, self.units, self.side_, self.contacts]
        return observation

    # XML Data Extraction Methods
    def get_meta(self) -> Game:
        """Get meta data (top-level scenario data)"""
        return Game(self.scen_dic['Scenario']["TimelineID"],
                        self.scen_dic['Scenario']["Time"],
                        self.scen_dic['Scenario']["Title"],
                        self.scen_dic['Scenario']["ZeroHour"],
                        self.scen_dic['Scenario']["StartTime"],
                        self.scen_dic['Scenario']["Duration"],
                        self.get_sides())

    def get_sides(self):
        """Get the number and names of all sides in a scenario"""
        return [self.scen_dic['Scenario']['Sides']['Side'][i]['Name'] for i in range(len(self.scen_dic['Scenario']['Sides']['Side']))]

    def get_side_properties(self, side_id = 0) -> Side:
        """Get the properties (score, name, etc.) of a side"""
        return Side(self.scen_dic['Scenario']['Sides']['Side'][side_id]['ID'],
                        self.scen_dic['Scenario']['Sides']['Side'][side_id]['Name'],
                        self.scen_dic['Scenario']['Sides']['Side'][side_id]['TotalScore'])

    def get_side_units(self, side_id_str=None):
        """Get all the units of a side"""
        if not side_id_str:
            return
        unit_ids = []
        for key in self.scen_dic["Scenario"]["ActiveUnits"].keys():
            if isinstance(self.scen_dic["Scenario"]["ActiveUnits"][key], list):
                for i in range(len(self.scen_dic["Scenario"]["ActiveUnits"][key])):
                    if "Side" in self.scen_dic["Scenario"]["ActiveUnits"][key][i].keys() and self.scen_dic["Scenario"]["ActiveUnits"][key][i]["Side"] == side_id_str:
                        id = self.scen_dic["Scenario"]["ActiveUnits"][key][i]['ID']
                        name = self.scen_dic["Scenario"]["ActiveUnits"][key][i]['Name']
                        dbid = self.scen_dic["Scenario"]["ActiveUnits"][key][i]['DBID']
                        loadout = None
                        if 'Loadout' in self.scen_dic["Scenario"]["ActiveUnits"][key][i].keys() and self.scen_dic["Scenario"]["ActiveUnits"][key][i]['Loadout'] != None:
                            loadout = self.get_loadout(key, i)
                        mount = None
                        if 'Mounts' in self.scen_dic["Scenario"]["ActiveUnits"][key][i].keys() and self.scen_dic["Scenario"]["ActiveUnits"][key][i]['Mounts'] != None:
                            mount = self.get_mount(key, i)
                        unit_ids.append(Unit(i, id, name, self.player_side, dbid, key, mount, loadout))
            else:
                if "Side" in self.scen_dic["Scenario"]["ActiveUnits"][key].keys() and self.scen_dic["Scenario"]["ActiveUnits"][key]["Side"] == side_id_str:
                    id = self.scen_dic["Scenario"]["ActiveUnits"][key]['ID']
                    name = self.scen_dic["Scenario"]["ActiveUnits"][key]['Name']
                    dbid = self.scen_dic["Scenario"]["ActiveUnits"][key]['DBID']
                    loadout = None
                    if 'Loadout' in self.scen_dic["Scenario"]["ActiveUnits"][key].keys() and self.scen_dic["Scenario"]["ActiveUnits"][key]['Loadout'] != None:
                        loadout = self.get_loadout(key)
                    mount = None
                    if 'Mounts' in self.scen_dic["Scenario"]["ActiveUnits"][key].keys() and self.scen_dic["Scenario"]["ActiveUnits"][key]['Mounts'] != None:       
                        mount = self.get_mount(key)
                    unit_ids.append(Unit(i, id, name, self.player_side, dbid, key, mount, loadout))
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

    def get_contacts(self, side_id = 0):
        try:
            contact_id = []
            contacts = self.scen_dic["Scenario"]["Sides"]["Side"][side_id]["Contacts"]["Contact"]
            for i in range(len(contacts)):
                try:
                    contact_id.append(Contact(i, contacts[i]["ID"]))
                except KeyError:
                    contact_id.append(Contact(0, contacts["ID"]))
            return contact_id
        except KeyError:
            return

if __name__ == '__main__':
    features = features_from_game_("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\wooden_leg.xml", "Israel")
    print(features.units['Aircraft'][0]['Lat'])
