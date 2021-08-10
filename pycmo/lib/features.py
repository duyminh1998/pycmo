"""Export Command raw data into numpy arrays."""

import xml.etree.ElementTree as ET
import xmltodict
import collections

# Game info
GameInfo = collections.namedtuple("GameInfo", ["TimelineID", "Time", "ScenarioName", "ZeroHour", "StartTime", "Duration", "Sides"])
# Side/Player info
# SideInfo = collections.namedtuple("SideInfo", ['ID', 'Name', 'Postures', 'ReferencePoints', 'Doctrine', 'TotalScore', 'Missions', 'Units'])
SideInfo = collections.namedtuple("SideInfo", ['ID', 'Name', 'Postures', 'Doctrine', 'TotalScore', 'Units'])
# Mission Info
# MsnInfo = collections.namedtuple("MsnInfo", [])
# Unit info
UnitInfo = collections.namedtuple("UnitInfo", ['ID', 'Name', 'CH', 'CS', 'Lon', 'Lat', 'LonLR', 'LatLR', 'Side', 'DBID', 'DH', 'DS', 'DT', 'DTN', 
'ThrottleSetting', 'Sensors', 'Comms', 'Mounts', 'Magazines', 'Status', 'FuelState', 'WeaponState', 'SBR', 'SBED', 'SBEO', 'FSBR', 'SBR_Altitude', 
'SBR_Altitude_TF', 'SBR_TF', 'SBR_ThrottleSetting', 'SBED_Altitude', 'SBED_Altitude_TF', 'SBED_TF', 'SBED_ThrottleSetting', 'SBEO_Altitude', 'SBEO_Altitude_TF', 
'SBEO_TF', 'SBEO_ThrottleSetting', 'AMP_OC', 'AMP_OC_DAO', 'AMP_OC_Speed', 'DamagePts', 'OldDamagePercent', 'Doctrine', 'CIC', 'Navigator', 'AI', 'Kinematics', 
'Sensory', 'Weaponry', 'CommStuff', 'Damage', 'ActiveUnit_AirOps', 'ActiveUnit_DockingOps'])
# Contacts info
ContactInfo = collections.namedtuple("ContactInfo", ["Name"])

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
            self.side_info = self.get_side_prop(self.meta.Sides.index(player_side))

    def transform_obs(self, obs):
        """Render some SC2 observations into something an agent can handle."""
        pass

    # XML Data Extraction Methods
    def get_meta(self):
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

    def get_side_prop(self, side_id = 0):
        """Get the properties of a side"""
        side = self.scen_dic['Scenario']['Sides']['Side'][side_id]
        return SideInfo(side['ID'], side['Name'], side['Postures'], "side['Doctrine']",
                        side['TotalScore'], "side['Units']")

    def get_side_units(self, side_id_str):
        """Get all the units of a side"""
        ar = {}
        ar[" "] = " "
        if side_id_str == " ":
            return ar
        for i in range(len(self.root[21])):
            for match in self.root[21][i].iterfind("Side"):
                if match.text == side_id_str:
                    if self.root[21][i][1].text not in ar.keys():
                        ar[self.root[21][i][1].text] = i
                    else:
                        j = 1
                        new_str = self.root[21][i][1].text + " #" + str(j)
                        while new_str in ar.keys():
                            j += 1
                            new_str = self.root[21][i][1].text + " #" + str(j)
                        ar[new_str] = i
                    break
        return collections.OrderedDict(sorted(ar.items()))

    def get_side_unit_prop(self, unit_id_str, side_units_ar = []):
        """Get the properties of a unit of a side"""
        if len(side_units_ar) < 1:
            side_units_ar = self.side_units_ar
        ar = {}
        if unit_id_str == " ":
            return ar
        for i in range(len(self.root[21][side_units_ar[unit_id_str]])):
            try:
                ar[self.root[21][side_units_ar[unit_id_str]][i].tag + ": " + self.root[21][side_units_ar[unit_id_str]][i].text] = i
            except TypeError:
                ar[self.root[21][side_units_ar[unit_id_str]][i].tag + ": "] = i
        return ar

    def get_side_doctrine(self, side_id = 0):
        """Get the doctrine of a side"""
        ar = {}
        for i in range(len(self.root[19][side_id][5])):
            try:
                ar[self.root[19][side_id][5][i].tag + ": " + self.root[19][side_id][5][i].text] = i
            except TypeError:
                ar[self.root[19][side_id][5][i].tag + ": "] = i
        return ar 

if __name__ == '__main__':
    features = features_from_game_info("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\wooden_leg.xml", "Israel")
    print(features.side_info)
