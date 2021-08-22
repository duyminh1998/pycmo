## Environment Table of Contents

- [Command Modern Operations](#command-modern-operations)
    - [What is Command Modern Operations](#what-is-cmo)
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
- [RL Environment](#rl-environment)
- [Agents](#agents)

<!-- /TOC -->

## Command Modern Operations

### What is Command Modern Operations

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

##### Contact
A named tuple containing information about a contact from the perspective of the player's side.  
`XML_ID`: the index of the contact within the scenario XML file  
`ID`: the in-game ID of the contact  
`CS`: the contact's current speed, if known  
`CA`: the contact's current altitude, if known  
`Lon`: the contact's current longitude, if known  
`Lat`: the contact's current latitude, if known

### Actions
`actions.py` defines the action space as a collection of Lua functions that gets sent to the game. It also defines `AvailableActions`, a class which contains actions that are available only at a particular timestep.

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

#### AvailableActions

## RL Environment

## Agents
* `RandomAgent`: Just plays randomly, shows how to make valid moves.
* `RuleBasedAgent`: Scripted for specific scenarios.
* `NeuralNetworkAgent`: WIP
