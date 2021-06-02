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
    
    def __init__():
        pass

    def transform_obs(self, obs):
        """Render some SC2 observations into something an agent can handle."""
        pass

if __name__ == '__main__':
    features_from_game_info("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\scen.xml")
