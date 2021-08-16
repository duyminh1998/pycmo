"""Export Command raw data into numpy arrays."""

import xml.etree.ElementTree as ET
import xmltodict
import collections

# Game info
GameInfo = collections.namedtuple("GameInfo", ["TimelineID", "Time", "ScenarioName", "ZeroHour", "StartTime", "Duration", "Sides"])
# Side/Player info
# SideInfo = collections.namedtuple("SideInfo", ['ID', 'Name', 'Postures', 'ReferencePoints', 'Doctrine', 'TotalScore', 'Missions', 'Units'])
SideInfo = collections.namedtuple("SideInfo", ['ID', 'Name', 'TotalScore'])
# Mission Info
# MsnInfo = collections.namedtuple("MsnInfo", [])
# Unit info
UnitIdentifier = collections.namedtuple("UnitIdentifier", ['XML_ID', 'ID', 'Name', 'Side', 'DBID', 'Type'])
# Contacts info
ContactInfo = collections.namedtuple("ContactInfo", ["XML_ID", "ID"])

def features_from_game_info(xml, side):
    """Construct a Features object using data extracted from game info."""
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
        self.meta = self.get_meta() # Return the scenario-level information of the scenario
        self.units = self.get_side_units(player_side)
        # self.unit_features = self.get_side_unit_features(player_side)
        player_side_index = self.get_sides().index(player_side)
        self.side_info = self.get_side_properties(player_side_index)
        self.contacts = self.get_contacts(player_side_index)
        # self.contact_features = self.get_contact_features(player_side_index)
        
    def transform_obs(self, obs):
        """Render some Command observations into something an agent can handle."""
        observation = [self.meta, self.units, self.side_info, self.contacts]
        return observation

    # XML Data Extraction Methods
    def get_meta(self) -> GameInfo:
        """Get meta data (top-level scenario data)"""
        return GameInfo(self.scen_dic['Scenario']["TimelineID"],
                        self.scen_dic['Scenario']["Time"],
                        self.scen_dic['Scenario']["Title"],
                        self.scen_dic['Scenario']["ZeroHour"],
                        self.scen_dic['Scenario']["StartTime"],
                        self.scen_dic['Scenario']["Duration"],
                        self.get_sides())

    def get_sides(self):
        """Get the number and names of all sides in a scenario"""
        return [self.scen_dic['Scenario']['Sides']['Side'][i]['Name'] for i in range(len(self.scen_dic['Scenario']['Sides']['Side']))]

    def get_side_properties(self, side_id = 0) -> SideInfo:
        """Get the properties (score, name, etc.) of a side"""
        return SideInfo(self.scen_dic['Scenario']['Sides']['Side'][side_id]['ID'],
                        self.scen_dic['Scenario']['Sides']['Side'][side_id]['Name'],
                        self.scen_dic['Scenario']['Sides']['Side'][side_id]['TotalScore'])

    def get_side_units(self, side_id_str=None):
        """Get all the units of a side"""
        if not side_id_str:
            return
        unit_ids = []
        for key in self.scen_dic["Scenario"]["ActiveUnits"].keys():
            for i in range(len(self.scen_dic["Scenario"]["ActiveUnits"][key])):
                try:
                    if self.scen_dic["Scenario"]["ActiveUnits"][key][i]["Side"] == side_id_str:
                        id = self.scen_dic["Scenario"]["ActiveUnits"][key][i]['ID']
                        name = self.scen_dic["Scenario"]["ActiveUnits"][key][i]['Name']
                        dbid = self.scen_dic["Scenario"]["ActiveUnits"][key][i]['DBID']
                        unit_ids.append(UnitIdentifier(i, id, name, self.player_side, dbid, key))
                except KeyError:
                    if self.scen_dic["Scenario"]["ActiveUnits"][key]["Side"] == side_id_str:
                        id = self.scen_dic["Scenario"]["ActiveUnits"][key]['ID']
                        name = self.scen_dic["Scenario"]["ActiveUnits"][key]['Name']
                        dbid = self.scen_dic["Scenario"]["ActiveUnits"][key]['DBID']
                        unit_ids.append(UnitIdentifier(i, id, name, self.player_side, dbid, key))
        return unit_ids

    def get_side_unit_features(self, side_id_str=None):
        """Get all the units features of a side"""
        if not side_id_str:
            return
        ar = []
        for unit in self.units:
            try:
                ar.append(self.scen_dic["Scenario"]["ActiveUnits"][unit.Type][unit.XML_ID])
            except KeyError:
                ar.append(self.scen_dic["Scenario"]["ActiveUnits"][unit.Type])
        return ar

    def get_contacts(self, side_id = 0):
        try:
            contact_id = []
            contacts = self.scen_dic["Scenario"]["Sides"]["Side"][side_id]["Contacts"]["Contact"]
            for i in range(len(contacts)):
                try:
                    contact_id.append(ContactInfo(i, contacts[i]["ID"]))
                except KeyError:
                    contact_id.append(ContactInfo(0, contacts["ID"]))
            return contact_id
        except KeyError:
            return

    def get_contact_features(self, side_id = 0):
        try:
            return self.scen_dic["Scenario"]["Sides"]["Side"][side_id]["Contacts"]
        except KeyError:
            return

    # helper methods

if __name__ == '__main__':
    features = features_from_game_info("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\wooden_leg_w_contacts.xml", "Israel")
    print(features.units)
