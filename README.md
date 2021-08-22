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
4. Navigate to "pycmo". Then, install the repository using `pip install .`

## Run an agent
1. Open a terminal within the game's directory and load a scenario in Interactive mode. For example, 
```
./CommandCLI.exe -mode I -scenfile "C:\ProgramData\Command Professional Edition 2\Scenarios\Standalone Scenarios\Wooden Leg, 1985.scen" -outputfolder "C:\ProgramData\Command Professional Edition 2\Analysis_Int"
```
2. Call `pycmo.run_loop.py` to run the main loop.

# Environment Details
For a full description of the specifics of how the environment is configured, the observations and action spaces work read the [environment documentation](https://github.com/duyminh1998/pycmo/blob/main/docs/environment.md).
