"""Export Command raw data into numpy arrays."""

import xml.etree.ElementTree as ET

def extract_observations(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    print("Time:", root[12].text)
    print("Duration:", root[15].text)
    print(root[19][1][1].text)
    for child in root[19]:
        print(child[1].text)

if __name__ == '__main__':
    extract_observations("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\scen.xml")
