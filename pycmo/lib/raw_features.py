"""Export Command xml data into raw data."""

import xml.etree.ElementTree as ET
import xmltodict

class Data(object):
    """Render Command xml file into arrays of raw data."""
    
    def __init__(self, xml):
        tree = ET.parse(xml) # This variable contains the XML tree
        root = tree.getroot() # This is the root of the XML tree
        xmlstr = ET.tostring(root)
        self.scen_dic = xmltodict.parse(xmlstr) # our scenario xml is now in 'dic'
        self.meta = self.get_meta() # Return the scenario-level information of the scenario

    # XML Data Extraction Methods
    def get_meta(self):
        """Get meta data (top-level scenario data)"""
        meta = self.scen_dic['Scenario']
        try:
            del meta['Sides']
            del meta['ActiveUnits']
            del meta['NonActiveUnits']
            del meta['EventTriggers']
            del meta['EventConditions']
            del meta['SimEvents']
            del meta['MessageLog']
            del meta['MessageIncrement']
        except:
            pass
        return meta

if __name__ == '__main__':
    features = Data("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\wooden_leg.xml")
    print(features.meta['TimelineID'])
