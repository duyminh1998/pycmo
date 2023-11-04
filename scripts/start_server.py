# Author: Minh Hua
# Date: 08/28/2021
# Purpose: Start a CMO server for the agents to connect to.

from pycmo.lib.protocol import Server
import sys

if __name__ == "__main__":
    try:
        args = sys.argv
        if len(args) == 2:
            scen = args[1]
            server = Server(scen)
            server.start_game()
    except:
        print("ERROR: unable to start game server.")
