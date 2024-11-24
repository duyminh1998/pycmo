![img](https://hb.imgix.net/05f49fdf2ca2abd4544cdb22345a4a9d29f11051.jpeg?auto=compress,format&fit=crop&h=353&w=616&s=9954ab723bba102a78aaaf27c930329c)

# PyCMO - Command Modern Operations Reinforcement Learning Environment

PyCMO is a reinforcement learning environment for Command Modern Operations written in Python. Using the premium edition's ability to output the current scenario to an XML file, PyCMO exposes the game as slices of observation, reward, and available actions at each timestep.

This project was submitted to the [NSIN AI for Command Challenge 2021](https://www.nsin.us/events/2021-07-05-ai-command/).

Read about the project in detail [here](https://minhhua.com/pycmo/).

# Prerequisites

1. Python 3.9.2
2. pip

# Quick Start Guide

## Get PyCMO

1. (Non-Steam, Premium edition only) Make sure the following settings are enabled in your Command Modern Operations' configurations (in `CPE.ini`):

```
[Lua]
EnableSocket = 1
SocketPort = 7777
AllowIO = 1
EncodingMode = 8
```

2. Click on "Clone or download", and then "Download Zip".
3. Unzip the repo anywhere.
4. Edit the project's `pycmo/configs/config_template.py` file to fit your system's paths, then rename it as `pycmo/configs/config.py` (IMPORTANT). You only need to edit the lines 8 - 11:

```python
pycmo_path = os.path.join("path/to", "pycmo")
cmo_path = os.path.join("path/to/steam/installation/of", "Command - Modern Operations")
command_mo_version = "Command v1.06 - Build 1328.12"
use_gymnasium = False
```

5. Navigate to the folder than contains `setup.py` and install the repository using `pip install .` Anytime you make changes to the files in the project folder, you need to reinstall the package using `pip install .`. Alternatively, use `pip install -e .` to install the package in editable mode. After doing this you can change the code without needing to continue to install it.
6. From PyCMO v1.4.0, [gymnasium](https://gymnasium.farama.org/) became an optional dependency for users who want to use PyCMO as a Gym environment. In this case, use `pip install .[gym]` or `pip install -e .[gym]` for setup. Remember to set `use_gymnasium = True` in the `pycmo/configs/config.py` file.

## Run an agent (Steam edition only)

1. Load the provided demo scenario `scen/steam_demo.scen` in the game.
2. Edit `scripts/steam_demo/init.lua` as needed and copy the contents to the in-game script editor and run the code (You only need to do this if your scenario does not have any events. If you are using the scenario from this repository then the events should have already been set up). This should set up events in the scenario to handle agent actions (which come from a Python script we run later) and regular exporting of observations. Save the scenario after you run the script and reload the scenario.
3. You might have to open the `pycmo/configs/config.py` file (create from `pycmo/configs/config_template.py` if file does not exist) and edit line 19 (`command_mo_version` variable) to whatever the version of Command you have (e.g. your build number or version might be different). This is needed for us to send commands to the game.
4. Run `scripts/steam_demo/demo.py`. The agent will control the `Sufa #1` aircraft and give it a random course every 6 seconds. Observations are exported every 5 seconds.

## Run an agent (Premium edition only)

1a. Open a terminal within the game's directory and load a scenario in Interactive mode. For example,

```
./CommandCLI.exe -mode I -scenfile "C:\ProgramData\Command Professional Edition 2\Scenarios\Standalone Scenarios\Wooden Leg, 1985.scen" -outputfolder "C:\ProgramData\Command Professional Edition 2\Analysis_Int"
```

1b. Alternatively, open a terminal anywhere and call `pycmo/lib/start_server.py` to start a scenario in Interactive mode. The path to the scenario must be supplied, e.g.

```
python pycmo/lib/start_server.py "C:\ProgramData\Command Professional Edition 2\Scenarios\Standalone Scenarios\Wooden Leg, 1985.scen"
```

2. Call `python pycmo/bin/agent.py` to run the main loop with the following arguments.

```
-agent AGENT        Select an agent. 0 for RandomAgent, 1 for ScriptedAgent, 2 for RuleBasedAgent.
-size SIZE          Size of a timestep, must be in "hh:mm:ss" format.
-scenario SCENARIO  The name of the scenario, used for ScriptedAgent and RuleBasedAgent. Usually the literal name of the .scen file.
-player PLAYER      The name of player's side.
```

The default is to run a RandomAgent on Wooden Leg with a timestep of 1 minute. Accepted scenario file names for the `-scenario` parameter above are

```
scenario_id = {
    'Operation Brass Drum, 2017',
    '2 - English Jets over Uganda, 1973',
    'Fighter Weapons School - GAT 5 and 6, 1977',
    'Iron Hand, 2014',
    'Khark Island Raid, 1985',
    'North Pacific Shootout, 1989',
    'Pyrpolitis 1-14, 2014',
    'Sea of Fire, 1982',
    'Shamal, 1991',
    'Task Force Normandy, 1991',
    'Wooden Leg, 1985',
    'None'
}
```

# Environment Details

For a full description of the specifics of how the environment is configured, the observations and action spaces work read the [environment documentation](https://github.com/duyminh1998/pycmo/blob/main/docs/environment.md).

# Related Work

- [A Reinforcement Learning Approach to Military Simulations in Command: Modern Operations](https://ieeexplore.ieee.org/document/10540085) (great example of a working reinforcement learning agent in Command)
