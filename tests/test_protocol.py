import pytest
import os

from pycmo.configs.config import get_config
from pycmo.lib.protocol import SteamClient, SteamClientProps

config = get_config()

scenario_name = "Steam demo"
agent_action_filename = os.path.join(config['pycmo_path'], 'tests', "fixtures", "test_python_agent_action.lua")
command_version = config["command_mo_version"]
steam_client_props = SteamClientProps(scenario_name = scenario_name, agent_action_filename=agent_action_filename, command_version=command_version)
client = SteamClient(props=steam_client_props)

def test_steam_client_init():
    assert isinstance(client, SteamClient)
    assert client.props.scenario_name == scenario_name
    assert client.cmo_window_title == f"{client.props.scenario_name} - {command_version}"

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

def test_steam_client_close_scenario_paused_message():
    assert client.connect() == True # have CMO running for this test to pass
    assert client.close_scenario_paused_message() == True

def test_steam_client_restart_scenario():
    assert client.connect() == True # have CMO running for this test to pass 
    assert client.restart_scenario() == True

def test_steam_client_close_scenario_end_and_player_eval_messages():
    assert client.connect() == True # have CMO running for this test to pass 
    assert client.close_scenario_end_and_player_eval_messages() == True

def test_steam_client_click_enter_scenario():
    assert client.connect() == True # have the "Side selection and briefing" window open for this test to pass
    assert client.click_enter_scenario() == True
