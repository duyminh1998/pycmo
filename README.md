![img](https://hb.imgix.net/05f49fdf2ca2abd4544cdb22345a4a9d29f11051.jpeg?auto=compress,format&fit=crop&h=353&w=616&s=9954ab723bba102a78aaaf27c930329c)
# PyCMO - Command Modern Operations Reinforcement Learning Environment
PyCMO is a reinforcement learning environment for Command Modern Operations written in Python. It exposes the game as slices of observation, reward, and available actions that get returned at each timestep. 

This project was submitted to the [NSIN AI for Command Challenge 2021](https://www.nsin.us/events/2021-07-05-ai-command/).

# Prerequisites
1. Python 3.9.2
2. pip

# Quick Start Guide
## Get PyCMO
1. Make sure the following settings are enabled in your Command Modern Operations' configurations (in `CPE.ini`):  
```
[Lua]
EnableSocket = 1
SocketPort = 7777
AllowIO = 1
EncodingMode = 8
```
2. Click on "Clone or download", and then "Download Zip". 
3. Unzip the repo anywhere.
4. Configure the project's `config.py` file to fit your system's paths. Do not change the amount of backslashes that are present in each entry as that could mess up its usage! If the `steps` directory is not present in `raw` then create it.
```python
{
    "command_path": "C:\\Program Files (x86)\\Command Professional Edition 2\\",
    "observation_path": "C:\\\\Users\\\\AFSOC A8XW ORSA\\\\Documents\\\\Python Proj\\\\AI\\\\pycmo\\\\raw\\\\steps\\\\",
    "scen_ended": "C:\\\\Users\\\\AFSOC A8XW ORSA\\\\Documents\\\\Python Proj\\\\AI\\\\pycmo\\\\pycmo\\\\configs\\\\scen_has_ended.txt",
    "command_cli_output_path": "C:\\ProgramData\\Command Professional Edition 2\\Analysis_Int"
}
```
5. Navigate to "pycmo". Then, navigate to the folder than contains `setup.py` and install the repository using `pip install .` Anytime you make changes to the files in the project folder, you need to reinstall the package using `pip install .`.

## Run an agent
1a. Open a terminal within the game's directory and load a scenario in Interactive mode. For example, 
```
./CommandCLI.exe -mode I -scenfile "C:\ProgramData\Command Professional Edition 2\Scenarios\Standalone Scenarios\Wooden Leg, 1985.scen" -outputfolder "C:\ProgramData\Command Professional Edition 2\Analysis_Int"
```
1b. Alternatively, open a terminal anywhere and call `start_server.py` to start a scenario in Interactive mode. The path to the scenario must be supplied, e.g.
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
The default is to run a RandomAgent on Wooden Leg with a timestep of 1 minute.

# Environment Details
For a full description of the specifics of how the environment is configured, the observations and action spaces work read the [environment documentation](https://github.com/duyminh1998/pycmo/blob/main/docs/environment.md).
