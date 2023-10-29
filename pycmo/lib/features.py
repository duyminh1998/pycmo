# Author: Minh Hua
# Date: 08/16/2021
# Last Update: 06/16/2022
# Purpose: Export Command raw data into Features object and flatten into agent-consummable data.

# imports
import xml.etree.ElementTree as ET
import xmltodict
import collections

# This section can be modified to dictate the type of observations that are returned from the game at each time step
# Game 
Game = collections.namedtuple("Game", ["TimelineID", "Time", "ScenarioName", "ZeroHour", "StartTime", "Duration", "Sides"])
# Side 
Side = collections.namedtuple("Side", ['ID', 'Name', 'TotalScore'])
# Unit 
Unit = collections.namedtuple("Unit", ['XML_ID', 'ID', 'Name', 'Side', 'DBID', 'Type',
                                        'CH', 'CS', 'CA', 'Lon', 'Lat', 'CurrentFuel', 'MaxFuel', 'Mounts', 'Loadout'])
# Mount 
Mount = collections.namedtuple("Mount", ["XML_ID", "ID", "Name", "DBID", "Weapons"])
# Loadout
Loadout = collections.namedtuple("Loadout", ["XML_ID", "ID", "Name", "DBID", "Weapons"])
# Weapon
Weapon = collections.namedtuple("Weapon", ["XML_ID", "ID", "WeaponID", "QuantRemaining", "MaxQuant"])
# Contacts 
Contact = collections.namedtuple("ContactInfo", ["XML_ID", "ID", 'Name', 'CS', 'CA', 'Lon', 'Lat'])

class Features(object):
    """
    Render feature layers from a Command: Professional Edition scenario XML into named tuples.
    """
    def __init__(self, xml:str, player_side:str) -> None:
        """
        Description:
            Initialize a Features object to hold observations.

        Keyword Arguments:
            xml: the path to the xml file containing the game observations.
            player_side: the side of the player. Dictates the units that they can actually control.
        
        Returns:
            None
        """
        try:
            tree = ET.parse(xml) # This variable contains the XML tree
            root = tree.getroot() # This is the root of the XML tree
            xmlstr = ET.tostring(root)            
            self.scen_dic = xmltodict.parse(xmlstr) # our scenario xml is now in 'dic'
        except FileNotFoundError as error:
            raise ValueError("Unable to parse scenario xml.")
        
        # get features
        self.player_side = player_side
        self.meta = self.get_meta() # Return the scenario-level rmation of the scenario
        self.avai_weapons = []
        self.units = self.get_side_units(player_side)
        try:
            player_side_index = self.get_sides().index(player_side)
        except:
            raise ValueError('Cannot find player side.')
        self.side_ = self.get_side_properties(player_side_index)
        self.contacts = self.get_contacts(player_side_index)
        
    def transform_obs_into_arrays(self) -> list:
        """
        Description:
            Render some Command observations into something an agent can handle.

        Keyword Arguments:
            None
        
        Returns:
            (list) a list of the game's meta data, units, side info, and contact info
        """
        observation = [self.meta, self.units, self.side_, self.contacts]
        return observation

    # ============== XML Data Extraction Methods ================================
    def get_meta(self) -> Game:
        """
        Description:
            Get meta data (top-level scenario data).

        Keyword Arguments:
            None
        
        Returns:
            (Game) a named tuple containing the meta data of the game.
        """
        try:
            return Game(self.scen_dic['Scenario']["TimelineID"],
                            self.scen_dic['Scenario']["Time"],
                            self.scen_dic['Scenario']["Title"],
                            self.scen_dic['Scenario']["ZeroHour"],
                            self.scen_dic['Scenario']["StartTime"],
                            self.scen_dic['Scenario']["Duration"],
                            self.get_sides())
        except KeyError:
            raise KeyError("Failed to get scenario properties.")

    def get_sides(self) -> list:
        """
        Description:
            Get the number and names of all sides in a scenario.

        Keyword Arguments:
            None
        
        Returns:
            (list) a list of side names
        """        
        try:
            return [self.scen_dic['Scenario']['Sides']['Side'][i]['Name'] for i in range(len(self.scen_dic['Scenario']['Sides']['Side']))]
        except KeyError:
            raise KeyError("Failed to get list of side names in scenario.")

    def get_side_properties(self, side_id:int=0) -> Side:
        """
        Description:
            Get the properties (score, name, etc.) of a side.

        Keyword Arguments:
            side_id: index to choose the side for information.
        
        Returns:
            (Side) a named tuple containing Side information.
        """
        try:
            return Side(self.scen_dic['Scenario']['Sides']['Side'][side_id]['ID'],
                        self.scen_dic['Scenario']['Sides']['Side'][side_id]['Name'],
                        int(self.scen_dic['Scenario']['Sides']['Side'][side_id]['TotalScore']))
        except KeyError:
            raise KeyError("Failed to get side properties.")

    def get_side_units(self, side_id_str=None) -> list:
        """
        Description:
            Get all the units of a side.

        Keyword Arguments:
            side_id_str: the name of the side to get units for.
        
        Returns:
            (list) a list of the units of the side.
        """
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

    def get_mount(self, unit_xml:dict) -> list:
        """
        Description:
            Returns the Mounts of a unit. Required to control the weapons on the unit.

        Keyword Arguments:
            unit_xml: the xml string of the unit. Preferably in dictionary format.
        
        Returns:
            (list) a list of the unit's mounts.
        """        
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

    def get_loadout(self, unit_xml:dict) -> Loadout:
        """
        Description:
            Returns the Loadout of a unit.

        Keyword Arguments:
            unit_xml: the xml string of the unit. Preferably in dictionary format.
        
        Returns:
            (Loadout) the unit's current loadout.
        """                
        loadout_xml = unit_xml["Loadout"]["Loadout"]
        loadout_id = loadout_xml["ID"]
        name = loadout_xml["Name"]
        dbid = loadout_xml["DBID"]
        return Loadout(0, loadout_id, name, dbid, self.get_weapon('Loadout', loadout_xml))
    
    def get_weapon(self, mount_or_loadout:str, xml_str:str):
        """
        Description:
            Returns the weapons on a mount or loadout. Also sets the unit's list of available weapons.

        Keyword Arguments:
            mount_or_loadout: str to determine whether we are getting weapons from a mount or a loadout.
            xml_str: the xml str of the unit.
        
        Returns:
            (list) the unit's weapons.
        """
        weapons = []
        if mount_or_loadout == "Loadout":
            if 'Weaps' not in xml_str.keys() or xml_str['Weaps'] == None:
                return weapons
            wrec = xml_str['Weaps']['WRec']
            if not isinstance(wrec, list):
                wrec = [xml_str['Weaps']['WRec']]
            for i in range(len(wrec)):
                cl = None
                ml = None
                if "CL" in wrec[i].keys():
                    cl = int(wrec[i]["CL"])
                if "ML" in wrec[i].keys():
                    ml = int(wrec[i]["ML"])            
                weapons.append(Weapon(i, wrec[i]["ID"], wrec[i]['WeapID'], cl, ml))
                self.avai_weapons.append(Weapon(i, wrec[i]["ID"], wrec[i]['WeapID'], cl, ml))
            return weapons
        elif mount_or_loadout == "Mount":
            if 'MW' not in xml_str.keys() or xml_str['MW'] == None:
                return weapons
            wrec = xml_str['MW']['WRec']
            if not isinstance(wrec, list):
                wrec = [xml_str['MW']['WRec']]
            for i in range(len(wrec)):
                cl = None
                ml = None
                if "CL" in wrec[i].keys():
                    cl = int(wrec[i]["CL"])
                if "ML" in wrec[i].keys():
                    ml = int(wrec[i]["ML"])                    
                weapons.append(Weapon(i, wrec[i]["ID"], wrec[i]['WeapID'], cl, ml))
                self.avai_weapons.append(Weapon(i, wrec[i]["ID"], wrec[i]['WeapID'], cl, ml))
            return weapons
        else:
            return weapons

    def get_contacts(self, side_id:int=0) -> list:
        """
        Description:
            Return the contacts of a side.

        Keyword Arguments:
            side_id: index to choose the side for information.
        
        Returns:
            (list) a list of contacts.
        """
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

class FeaturesFromSteam(object):
    """
    Renders feature layers from a Command: Modern Operations scenario XML into named tuples.
    """
    def __init__(self, xml:str, player_side:str) -> None:
        """
        Description:
            Initialize a Features object to hold observations.

        Keyword Arguments:
            xml: the path to the xml file containing the game observations.
            player_side: the side of the player. Dictates the units that they can actually control.
        
        Returns:
            None
        """
        try:         
            self.scen_dic = xmltodict.parse(xml) # our scenario xml is now in 'dic'
        except FileNotFoundError as error:
            raise ValueError("Unable to parse scenario xml.")
        
        # get features
        self.player_side = player_side
        # self.meta = self.get_meta() # Return the scenario-level rmation of the scenario
        # self.avai_weapons = []
        # self.units = self.get_side_units(player_side)
        # try:
        #     player_side_index = self.get_sides().index(player_side)
        # except:
        #     raise ValueError('Cannot find player side.')
        # self.side_ = self.get_side_properties(player_side_index)
        # self.contacts = self.get_contacts(player_side_index)
