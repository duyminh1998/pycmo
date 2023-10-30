## Environment Table of Contents

- [Command Modern Operations](#command-modern-operations)
    - [What is Command Modern Operations](#what-is-cmo)
- [RL Environment](#rl-environment)
- [Actions and Observations](#actions-and-observations)
    - [Observation](#observations)
        - [Features](#features)
            - [Game](#game)
            - [Side](#side)
            - [Unit](#unit)
            - [Mount](#mount)
            - [Loadout](#loadout)
            - [Weapon](#weapon)
            - [Contact](#contact)
    - [Actions](#actions)
        - [List of actions](#list-of-actions)
        - [Example usage](#example-usage)
- [Agents](#agents)

<!-- /TOC -->

## Command Modern Operations

### What is Command Modern Operations
Command: Modern Operations is a modern wargaming game that enables you to simulate every military engagement from post World War II to the present day and beyond. The scale is primarily tactical/operational, although strategic scale operations are also possible. Players control units on a side to achieve scenario objectives and score points. Units can be controlled directly or assigned to missions such as Patrol, Strike, Ferry, etc.

## RL Environment
The reinforcement learning environment is broken into two parts. The first part is the `Server` that starts the game in Interactive mode in order for agents to be able to connect and send commands to. The `Server` should always be started first before the second part of the environment. To do this, either call `pycmo/lib/start_server.py` with a corresponding path to the scenario you want to load, or just start the game in Interactive mode using a terminal (this is simply what `start_server.py` does). After the scenario has been loaded, players need to call `pycmo/bin/agent.py`, which will call `pycmo/lib/run_loop.py`, the main loop that consists of observation gathering and agent sending actions.

`run_loop.py` first locates the `raw/steps` folder in order to save the scenario XML file at each timestep; it cleans up the folder for any leftover step files from the previous run. Then, if the `server` parameter is specified, then it will also start a `Server` and load a scenario. We do not recommend using this feature as it can lead to timing issues, e.g. the `Server` takes a few seconds to load before the agent can connect to it. Next, a `CPEEnv` object is created which will represent our environment. The `CPEEnv` is used to step through the game, get observations, and return the available actions to the agent. We gather observations at each timestep by calling `ScenEdit_ExportScenarioToXML()` at each timestep in the game, and processing the output XML file using `features.py` (more in detail below). In the last loop of `run_loop.py`, we get observations and available actions, let our agent choose an action, step the environment forward with the chosen action, and get the observation of the resulting new state. We have defined 8 actions that are available to the agent at each timestep, to include launching, refueling, and striking targets, but have made the parameter space large enough to encompass the whole scenario.

## Actions and Observations

### Observation

#### Features
`Features` is a class in `pycmo.lib.features` that renders information from the game into the named tuples listed below. At each timestep, the main loop wraps the game's observation into a `Features` object. Observations are loaded into `Features` during initialization, so there is no need to query for specific observations after initialization. `Features` takes as input 2 required arguments: `xml` and `player_side`. `xml` is the XML file generated from the game that contains information at a particular timestep. `Features` uses the module `xmltodict` to parse `xml` and record the data. `player_side` is a String that defines the agent's side in the game. `Features` is an object that is unique to a particular side, so it will not hold information about other sides that a side would not usually know.

##### Game
A named tuple containing scenario-level information about the game. `Time` is mainly used to get the scenario's current time.  
`TimelineID`: the ID of the current scenario iteration  
`Time`: the current time of the scenario  
`ScenarioName`: the name of the current scenario  
`ZeroHour`: the start time of the scenario in zero hour  
`StartTime`: the start time of the scenario in unix  
`Duration`: the total duration of the scenario in seconds  
`Sides`: an array of the sides in the current scenario. Only the names are recorded.

##### Side
A named tuple containing information about a particular side.  
`ID`: the ID of the player's side  
`Name`: the name of the player's side  
`TotalScore`: the current score of the player's side

##### Unit
A named tuple containing information about a specific unit.  
`XML_ID`: the index of the unit within the scenario XML file  
`ID`: the in-game ID of the unit. This is used in Lua function actions  
`Name`: the name of the unit  
`Side`: the side of the unit  
`DBID`: the database ID of the unit  
`Type`: the type of unit. Usually (Ship, Aircraft, Facility, Submarine)  
`CH`:  
`CS`: the unit's current speed  
`CA`: the unit's current altitude  
`Lon`: the longitude position of the unit  
`Lat`:  the latitude position of the unit  
`CurrentFuel`: the unit's current fuel amount  
`MaxFuel`: the unit's max fuel amount  
`Mounts`: a list of `Mount` on the unit  
`Loadout`: the unit's `Loadout`

##### Mount
A named tuple containing information about a specific mount.  
`XML_ID`: the index of the mount within the scenario XML file  
`ID`: the in-game ID of the mount. This is used in Lua function actions    
`Name`: the name of the mount  
`DBID`: the database ID of the mount  
`Weapons`: a list of `Weapon` on the mount

##### Loadout
A named tuple containing information about a specific loadout.  
`XML_ID`: the index of the loadout within the scenario XML file  
`ID`: the in-game ID of the loadout. This is used in Lua function actions    
`Name`: the name of the loadout    
`DBID`: the database ID of the loadout   
`Weapons`: a list of `Weapon` on the loadout

##### Weapon
A named tuple containing information about a specific weapon.  
`XML_ID`: the index of the weapon within the scenario XML file  
`ID`: the in-game ID of the weapon  
`WeaponID`: the WeaponID of the weapon. This is used in Lua function actions  
`QuantRemaining`: the remaining quantity of the weapon  
`MaxQuant`: the weapon's maximum quantity

##### Contact
A named tuple containing information about a contact from the perspective of the player's side.  
`XML_ID`: the index of the contact within the scenario XML file  
`ID`: the in-game ID of the contact  
`Name`: the contact's name, if known  
`CS`: the contact's current speed, if known  
`CA`: the contact's current altitude, if known  
`Lon`: the contact's current longitude, if known  
`Lat`: the contact's current latitude, if known

### Actions
`actions.py` defines the action space as a collection of Lua functions that gets sent to the game. It also defines `AvailableActions`, a class which contains actions that are available only at a particular timestep. Thus, `AvailableActions` must be initialized with a `Features` object.

`Function` is a named tuple that defines an action within PyCMO. Every action has an `id`, a `name`, a Lua expression-equivalent (`corresponding_def`), arguments (`args`), and the argument types (`arg_types`).

#### List of actions
`no_op`: represents no action  
`launch_aircraft`: launches an aircraft from its base  
`set_unit_course`: directs a unit to travel to a specific waypoint  
`manual_attack_contact`: directs a unit to attack a contact with specific weapons  
`auto_attack_contact`: directs a unit to automatically attack a contact  
`refuel_unit`: directs a unit to refuel with a specific tanker  
`rtb`: directs a unit to return to base  
`auto_refuel`: directs a unit to automatically refuel with any tanker

#### Example usage
The function `set_unit_course` has the arguments `[sides, units, [-90, 90], [-180, 180]]` with corresponding argument types `['EnumChoice', 'EnumChoice', 'Range', 'Range']`. This means that for the arguments `sides` and `units`, an agent is expected to pick a value from a list of possible values. For the `Range` argument type, an agent is expected to pick a value within a numerical range. For a random agent, these values are sampled randomly and then fed back into `corresponding_def`, which is the Lua function that corresponds to that particular `Function`. Thus, if we had
```
sides = ["Israel", "Iran"]
untis = ["Unit #1", "Unit #2"]
lat = [-90, 90]
lon = [-180, 180]
```
our constructed `set_unit_course` function might be 
```
--script 
Tool_EmulateNoConsole(true) 
ScenEdit_SetUnit({side = 'Israel', name = 'Unit #1', course = {{longitude = '-12', latitude = '10', TypeOf = 'ManualPlottedCourseWaypoint'}}})
```

#### AvailableActions
As mentioned above, `AvailableActions` holds all the possible actions valid to a certain timestep. After initialization, the `VALID_FUNCTIONS` variable should be accessed to determine the corresponding valid functions. At each timestep, every action is valid but for only a certain subset of arguments, e.g. if a unit is dead then it will not show up as an argument.

## Agents
Each agent needs to have a `get_action` function that takes in a `Features` observation and a list of available actions (`VALID_FUNCTIONS`).
* `RandomAgent`: Just plays randomly, shows how to make valid moves.
* `ScriptedAgent`: Scripted for specific scenarios.  
* `RuleBasedAgent`: Decides actions according to rules.
* `NeuralNetworkAgent`: WIP. Ideally modelled after DeepMind's [AlphaStar](https://deepmind.com/blog/article/alphastar-mastering-real-time-strategy-game-starcraft-ii).

### Usage
Call `python pycmo/bin/agent.py` with the following arguments to run specific agents.
```
-agent AGENT        Select an agent. 0 for RandomAgent, 1 for ScriptedAgent, 2 for RuleBasedAgent.
-size SIZE          Size of a timestep, must be in "hh:mm:ss" format.
-scenario SCENARIO  The name of the scenario, used for ScriptedAgent and RuleBasedAgent. Usually the literal name of the .scen file.
-player PLAYER      The name of player's side.
```
The default is to run a RandomAgent on Wooden Leg with a timestep of 1 minute.
