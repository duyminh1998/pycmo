"""Export Command raw data into numpy arrays."""

import xml.etree.ElementTree as ET
import collections

# Game info
GameInfo = collections.namedtuple("GameInfo", ["Timeline ID", "Time", "Scenario Name", "Zero Hour", "Start Time", "Duration", "Sides", "Weather",
                                                "Events", "Time Compression", "Game Resolution"])

# Side/Player info
SideInfo = collections.namedtuple("SideInfo", ["ID", "Name", "Postures", "Doctrine", "Total Score", "Contacts", "Missions", "Human", "Units"])
# Unit info
UnitInfo = collections.namedtuple("UnitInfo", ["Name"])
# Contacts info
ContactInfo = collections.namedtuple("ContactInfo", ["Name"])

def features_from_game_info(xml):
    """Construct a Features object using data extracted from game info."""
    tree = ET.parse(xml)
    root = tree.getroot()
    # Game info


    print("Time:", root[12].text)
    print("Duration:", root[15].text)
    print(root[19][1][1].text)
    for child in root[19]:
        print(child[1].text)

class Features(object):
    """Render feature layers from SC2 Observation protos into numpy arrays.

        This has the implementation details of how to render a starcraft environment.
        It translates between agent action/observation formats and starcraft
        action/observation formats, which should not be seen by agent authors. The
        starcraft protos contain more information than they should have access to.

        This is outside of the environment so that it can also be used in other
        contexts, eg a supervised dataset pipeline."""
    
    def __init__(self, xml):
        try:
            self.tree = ET.parse(xml) # This variable contains the XML tree
            self.root = self.tree.getroot() # This is the root of the XML tree
            meta = self.get_meta()
            self.meta = GameInfo(meta[0])
        except:
            # Raise error can't find XML
            self.tree = ""
            self.root = ""

    def transform_obs(self, obs):
        """Render some SC2 observations into something an agent can handle."""
        pass

    # XML Data Extraction Methods
    def get_meta(self):
        """Get meta data (top-level scenario data)"""
        meta_ar = {}
        meta_ar[" "] = " "
        for i in range(19):
            try:
                meta_ar[self.root[i].tag + ": " + self.root[i].text] = i
            except TypeError:
                meta_ar[self.root[i].tag + ": "] = i
        return meta_ar

    def get_sides(self):
        """Get the number and names of all sides in a scenario"""
        sides_ar = {}
        sides_ar[" "] = " "
        for i in range(len(self.root[19])):
            sides_ar[self.root[19][i][1].text] = i
        return sides_ar

    def get_side_prop(self, side_id = 0):
        """Get the properties of a side"""
        ar = {}
        if side_id == " ":
            return ar
        for i in range(3):
            try:
                ar[self.root[19][side_id][i].tag + ": " + self.root[19][side_id][i].text] = i
            except TypeError:
                ar[self.root[19][side_id][i].tag + ": "] = i
        return ar

    def get_side_msn(self, side_id = 0):
        """Get the missions of a side"""
        ar = {}
        ar[" "] = " "
        if side_id == " ":
            return ar
        for i in range(len(self.root[19][side_id][12])):
            ar[self.root[19][side_id][12][i][1].text] = i
        return ar

    def get_side_msn_prop(self, side_id = 0, msn_id = 0):
        """Get the properties of a mission of a side"""
        ar = {}
        if msn_id == " ":
            return ar
        for i in range(len(self.root[19][side_id][12][msn_id])):
            try:
                ar[self.root[19][side_id][12][msn_id][i].tag + ": " + self.root[19][side_id][12][msn_id][i].text] = i
            except TypeError:
                ar[self.root[19][side_id][12][msn_id][i].tag + ": "] = i
        return ar

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
        if side_id == " ":
            return ar
        for i in range(len(self.root[19][side_id][5])):
            try:
                ar[self.root[19][side_id][5][i].tag + ": " + self.root[19][side_id][5][i].text] = i
            except TypeError:
                ar[self.root[19][side_id][5][i].tag + ": "] = i
        return ar

    def get_side_rp(self, side_id = 0):
        """Get the reference points of a side"""
        ar = {}
        ar[" "] = " "
        if side_id == " ":
            return ar
        for i in range(len(self.root[19][side_id][4])):
            ar[self.root[19][side_id][4][i][4].text] = i
        return ar        

    def get_side_rp_prop(self, side_id = 0, rp_id = 0):
        """Get the properties of a reference point of a side"""
        ar = {}
        if rp_id == " ":
            return ar
        for i in range(len(self.root[19][side_id][4][rp_id])):
            try:
                ar[self.root[19][side_id][4][rp_id][i].tag + ": " + self.root[19][side_id][4][rp_id][i].text] = i
            except TypeError:
                ar[self.root[19][side_id][4][rp_id][i].tag + ": "] = i
        return ar    

if __name__ == '__main__':
    features_from_game_info("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\scen.xml")
