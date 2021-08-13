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
""" UnitInfo = collections.namedtuple("UnitInfo", ['ID', 'Name', 'CH', 'CS', 'Lon', 'Lat', 'LonLR', 'LatLR', 'Side', 'DBID', 'DH', 'DS', 'DT', 'DTN', 
'ThrottleSetting', 'Sensors', 'Comms', 'Mounts', 'Magazines', 'Status', 'FuelState', 'WeaponState', 'SBR', 'SBED', 'SBEO', 'FSBR', 'SBR_Altitude', 
'SBR_Altitude_TF', 'SBR_TF', 'SBR_ThrottleSetting', 'SBED_Altitude', 'SBED_Altitude_TF', 'SBED_TF', 'SBED_ThrottleSetting', 'SBEO_Altitude', 'SBEO_Altitude_TF', 
'SBEO_TF', 'SBEO_ThrottleSetting', 'AMP_OC', 'AMP_OC_DAO', 'AMP_OC_Speed', 'DamagePts', 'OldDamagePercent', 'Doctrine', 'CIC', 'Navigator', 'AI', 'Kinematics', 
'Sensory', 'Weaponry', 'CommStuff', 'Damage', 'ActiveUnit_AirOps', 'ActiveUnit_DockingOps']) """
# Contacts info
# ContactInfo = collections.namedtuple("ContactInfo", ["Name"])

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
        self.scen_dic = xmltodict.parse(xmlstr) # our scenario xml is now in 'dic'
        self.meta = self.get_meta() # Return the scenario-level information of the scenario
        self.units = self.get_side_units(player_side)
        player_side_index = self.get_sides().index(player_side)
        self.side_info = self.get_side_properties(player_side_index)
        self.contacts = self.get_contacts(player_side_index)

    def transform_obs(self, obs):
        """Render some Command observations into something an agent can handle."""
        pass

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
        ar = {}
        ar['Aircraft'] = []
        ar['Facility'] = []
        ar['Ship'] = []
        ar['Group'] = []
        ar['Submarine'] = []
        for key in self.scen_dic["Scenario"]["ActiveUnits"].keys():
            for i in range(len(self.scen_dic["Scenario"]["ActiveUnits"][key])):
                try:
                    if self.scen_dic["Scenario"]["ActiveUnits"][key][i]["Side"] == side_id_str:
                        ar[key].append(self.scen_dic["Scenario"]["ActiveUnits"][key][i])
                except KeyError:
                    if self.scen_dic["Scenario"]["ActiveUnits"][key]["Side"] == side_id_str:
                        ar[key].append(self.scen_dic["Scenario"]["ActiveUnits"][key])
        return ar

    def get_contacts(self, side_id = 0):
        try:
            return self.scen_dic["Scenario"]["Sides"]["Side"][side_id]["Contacts"]
        except KeyError:
            return

    # helper methods

if __name__ == '__main__':
    features = features_from_game_info("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\0.xml", "Israel")
    print(features.units['Aircraft'][0]['Lat'])
