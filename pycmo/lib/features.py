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
                                        'CH', 'CS', 'CA', 'Lon', 'Lat', 'CurrentFuel', 'MaxFuel', 'Mounts', 'Loadout'])
# add fuel
# Mount 
Mount = collections.namedtuple("Mount", ["XML_ID", "ID", "Name", "DBID", "Weapons"])
# Loadout
Loadout = collections.namedtuple("Loadout", ["XML_ID", "ID", "Name", "DBID", "Weapons"])
# Weapon
Weapon = collections.namedtuple("Weapon", ["XML_ID", "ID", "WeaponID", "QuantRemaining"])
# Contacts 
Contact = collections.namedtuple("ContactInfo", ["XML_ID", "ID", 'Name', 'CS', 'CA', 'Lon', 'Lat'])

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
        self.avai_weapons = []
        self.units = self.get_side_units(player_side)
        try:
            player_side_index = self.get_sides().index(player_side)
        except:
            print('ERROR: Cannot find player side')
            raise
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
                            int(self.scen_dic['Scenario']['Sides']['Side'][side_id]['TotalScore']))
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
                try:
                    if active_units[i]["Side"] == side_id_str:
                        unit_id = active_units[i]['ID']
                        name = active_units[i]['Name']
                        dbid = active_units[i]['DBID']
                        lon = float(active_units[i]['LonLR'])
                        lat = float(active_units[i]['LatLR'])
                        ch = None
                        cs = None
                        ca = None
                        loadout = None
                        mount = None
                        cf = None
                        mf = None
                        if 'Loadout' in active_units[i].keys() and active_units[i]['Loadout'] != None:
                            loadout = self.get_loadout(active_units[i])
                        if 'Mounts' in active_units[i].keys() and active_units[i]['Mounts'] != None:
                            mount = self.get_mount(active_units[i])
                        if 'CH' in active_units[i].keys() and active_units[i]['CH'] != None:
                            ch = active_units[i]['CH']
                        if 'CS' in active_units[i].keys() and active_units[i]['CS'] != None:
                            cs = float(active_units[i]['CS'])
                        if 'CA' in active_units[i].keys() and active_units[i]['CA'] != None:
                            ca = float(active_units[i]['CA'])
                        if 'Fuel' in active_units[i].keys():
                            cf = float(active_units[i]['Fuel']['FuelRec']['CQ'])
                            mf = float(active_units[i]['Fuel']['FuelRec']['MQ'])
                        unit_ids.append(Unit(i, unit_id, name, self.player_side, dbid, key, ch, cs, ca, lon, lat, cf, mf, mount, loadout))
                except KeyError:
                    pass                        
        return unit_ids

    def get_mount(self, unit_xml):
        mounts = []
        mount_xml = unit_xml["Mounts"]["Mount"]
        if not isinstance(mount_xml, list):
            mount_xml = [unit_xml["Mounts"]["Mount"]]
        for i in range(len(mount_xml)):
            mount_id = mount_xml[i]["ID"]
            name = mount_xml[i]["Name"]
            dbid = mount_xml[i]["DBID"]
            mounts.append(Mount(i, mount_id, name, dbid, self.get_weapon('Mount', mount_xml[i])))
        return mounts      

    def get_loadout(self, unit_xml):
        loadout_xml = unit_xml["Loadout"]["Loadout"]
        loadout_id = loadout_xml["ID"]
        name = loadout_xml["Name"]
        dbid = loadout_xml["DBID"]
        return Loadout(0, loadout_id, name, dbid, self.get_weapon('Loadout', loadout_xml))
    
    def get_weapon(self, mount_or_loadout: str, xml_str: str):
        weapons = []
        if mount_or_loadout == "Loadout":
            if 'Weaps' not in xml_str.keys() or xml_str['Weaps'] == None:
                return weapons
            wrec = xml_str['Weaps']['WRec']
            if not isinstance(wrec, list):
                wrec = [xml_str['Weaps']['WRec']]
            for i in range(len(wrec)):
                cl = None
                if "CL" in wrec[i].keys():
                    cl = int(wrec[i]["CL"])               
                weapons.append(Weapon(i, wrec[i]["ID"], wrec[i]['WeapID'], cl))
                self.avai_weapons.append(Weapon(i, wrec[i]["ID"], wrec[i]['WeapID'], cl))
            return weapons
        elif mount_or_loadout == "Mount":
            if 'MW' not in xml_str.keys() or xml_str['MW'] == None:
                return weapons
            wrec = xml_str['MW']['WRec']
            if not isinstance(wrec, list):
                wrec = [xml_str['MW']['WRec']]
            for i in range(len(wrec)):
                cl = None
                if "CL" in wrec[i].keys():
                    cl = int(wrec[i]["CL"])
                weapons.append(Weapon(i, wrec[i]["ID"], wrec[i]['WeapID'], cl))
                self.avai_weapons.append(Weapon(i, wrec[i]["ID"], wrec[i]['WeapID'], cl))
            return weapons
        else:
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
                    cont_name = None
                    if 'CS' in contacts[i].keys() and contacts[i]['CS'] != None:
                        cs = float(contacts[i]['CS'])
                    if 'CA' in contacts[i].keys() and contacts[i]['CA'] != None:
                        ca = float(contacts[i]['CA'])
                    if 'Lon' in contacts[i].keys() and contacts[i]['Lon'] != None:
                        lon = float(contacts[i]['Lon'])
                    if 'Lat' in contacts[i].keys() and contacts[i]['Lat'] != None:
                        lat = float(contacts[i]['Lat'])
                    if 'Name' in contacts[i].keys() and contacts[i]['Name'] != None:
                        cont_name = contacts[i]['Name']
                    contact_id.append(Contact(i, contacts[i]["ID"], cont_name, cs, ca, lon, lat))
                return contact_id
            else:
                return contact_id
        except KeyError:
            print("KeyError: failed to get side contacts.")
            return contact_id
        except:
            print("ERROR: failed to get side contacts.")
            return contact_id
