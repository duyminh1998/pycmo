"""A run loop for agent/environment interaction."""

from pycmo.lib.client import Client
from pycmo.lib.server import Server
import threading

client = Client()
server = Server("C:\\Program Files (x86)\\Command Professional Edition\\Scenarios\\Standalone Scenarios\\Battle of Chumonchin Chan, 1950.scen")

x = threading.Thread(target=server.start_game)
x.start()

for i in range(5):
    client.get_raw_data("C:\\Users\\Public\\Desktop\\scenario" + str(i) + ".xml")