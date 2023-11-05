import pytest
import os

from pycmo.configs.config import get_config
from pycmo.lib.protocol import SteamClient

config = get_config()

scenario_name = "Steam demo"
agent_action_filename = os.path.join(config['pycmo_path'], 'tests', "fixtures", "test_python_agent_action.lua")
command_version = config["command_mo_version"]
restart_duration = 6
client = SteamClient(scenario_name=scenario_name, 
                        agent_action_filename=agent_action_filename, 
                        command_version=command_version,
                        restart_duration=restart_duration)

def test_steam_client_init():
    assert isinstance(client, SteamClient)
    assert client.scenario_name == scenario_name
    assert client.cmo_window_title == f"{client.scenario_name} - {command_version}"

def test_steam_client_send():
    with open(agent_action_filename, 'w') as f:
        f.write("")
    
    action = "print('hello world')"

    assert client.send(action) == True

    with open(agent_action_filename, 'r') as f:
        assert f.read() == action

# these tests can only be run when Command is open
def test_steam_client_connect():
    assert client.connect() == True # have CMO running for this test to pass 

def test_steam_client_start_scenario():
    assert client.connect() == True # have CMO running for this test to pass 
    assert client.start_scenario() == True

def test_steam_client_close_scenario_message():
    assert client.connect() == True # have CMO running for this test to pass 
    assert client.close_scenario_message() == True

def test_steam_client_restart_scenario():
    assert client.connect() == True # have CMO running for this test to pass 
    assert client.restart_scenario() == True