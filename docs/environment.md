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

##### Mount

##### Loadout

##### Weapon

##### Contact
A named tuple containing information about a contact from the perspective of the player's side.
`XML_ID`: the index of the contact within the scenario XML file  
`ID`: the in-game ID of the contact  
`CS`: the contact's current speed, if known  
`CA`: the contact's current altitude, if known  
`Lon`: the contact's current longitude, if known  
`Lat`: the contact's current latitude, if known

### Actions

#### List of actions

#### Example usage

## RL Environment

## Agents
