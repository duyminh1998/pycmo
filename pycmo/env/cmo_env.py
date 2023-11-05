# Author: Minh Hua
# Date: 08/16/2021
# Last Update: 06/16/2022
# Purpose: A Command environment.

# imports
from pycmo.lib import actions
from pycmo.lib.features import Features, FeaturesFromSteam
from pycmo.lib.protocol import Client, SteamClient
from pycmo.lib.tools import cmo_steam_observation_file_to_xml
import collections, enum
import time, os

class TimeStep(
    collections.namedtuple(
        "TimeStep", ["step_id", "step_type", "reward", "observation"]
    )
):
    """
    Description:
        Returned with every call to `step` and `reset` on an environment.
        
        A `TimeStep` contains the data emitted by an environment at each step of
        interaction. A `TimeStep` holds a `step_type`, an `observation`, and an
        associated `reward` and `discount`.
        
        The first `TimeStep` in a sequence will have `StepType.FIRST`. The final
        `TimeStep` will have `StepType.LAST`. All other `TimeStep`s in a sequence will
        have `StepType.MID.

    Attributes:
        step_id: A scalar that represents the ID of a step.
        step_type: A `StepType` enum value.
        reward: A scalar, or 0 if `step_type` is `StepType.FIRST`, i.e. at the start of a sequence.
        observation: A NumPy array, or a dict, list or tuple of arrays.

    Author:
        DeepMind
    """

    def first(self):
        return self.step_type is StepType.FIRST

    def mid(self):
        return self.step_type is StepType.MID

    def last(self):
        return self.step_type is StepType.LAST

class StepType(enum.IntEnum):
    """
    Description:
        Defines the status of a `TimeStep` within a sequence.

    Author:
        DeepMind
    """

    # Denotes the first `TimeStep` in a sequence.
    FIRST = 0
    # Denotes any `TimeStep` in a sequence that is not FIRST or LAST.
    MID = 1
    # Denotes the last `TimeStep` in a sequence.
    LAST = 2

class CPEEnv():
    """
    A wrapper that extracts observations from and sends actions to Command: Professional Edition.
    """
    def __init__(self, step_dest: str, step_size: list, player_side: str, scen_ended_path: str) -> None:
        """
        Description:
            Initializes the environment for one session.

        Keyword Arguments:
            step_dest: the path of the folder to hold the steps.
            step_size: a list containing the step size in the format ["h", "m", "s"].
            player_side: the string identifying the player's side. Side should exist in the game.
            scen_ended_path: the path to the text file that records whether a scenario has ended or not.

        Returns:
            None
        """
        self.client = Client() # initialize a client to send data to the game
        self.client.connect() # connect the client to the game
        self.player_side = player_side # the player's side, this is used to identify units that the player can actually control
        self.step_dest = step_dest # the path to the folder containing the xml steps files. These steps files are used to generate observations.
        self.scen_ended = scen_ended_path # the path to the text file recording whether or not the scenario has ended. "hacky" way to determine when a scenario ends because the current Lua command for this check is buggy in-game.
        # the step size in h, m, s
        self.h = step_size[0]
        self.m = step_size[1]
        self.s = step_size[2]

    def reset(self) -> TimeStep:
        """
        Description:
            Starts a new sequence and returns the first TimeStep of this sequence.

        Keyword Arguments:
            None
        
        Returns:
            (TimeStep) named tuple containing step_id, step_type, reward, observation.
        """
        f = open(self.scen_ended, 'w') # note in the scenario has ended file that the scenario has ended
        f.write('False')
        return TimeStep(0, StepType(0), 0, self.get_obs(0)) # return initial time step

    def step(self, cur_time, step_id, action=None) -> TimeStep:
        """
        Description:
            Updates the environment according to the action and returns a `TimeStep`. 

        Keyword Arguments:
            cur_time: the current time, used to check whether the game has finished progressing so that we can get the observation. Must be converted to UNIX format because the game uses C# ticks.
            step_id: the current step ID.
            action: a string containing the Lua script to send to the environment.
        
        Returns:
            (TimeStep) named tuple containing step_id, step_type, reward, observation. 
        """
        # send the agent's action
        if action != None:
            self.client.send(action)

        # step the environment forwards
        self.client.send("\nVP_RunForTimeAndHalt({Time='" + str(self.h) + ":" + str(self.m) + ":" + str(self.s) + "'})")

        # get the corresponding observation and reward
        # continuously poll the game until the correct time step duration has passed
        paused = False
        dur_in_secs = (int(self.h) * 3600) + (int(self.m) * 60) + int(self.s)
        step_file_name = str(step_id) + '.xml'
        while not (paused or self.check_game_ended()):
            data = "--script \nlocal now = ScenEdit_CurrentTime() \nlocal elapsed = now - {} \nif elapsed >= {} then \nfile = io.open('{}', 'w') \nio.output(file) \ntheXML = ScenEdit_ExportScenarioToXML()\nio.write(theXML) \nio.close(file) \nend".format(cur_time, dur_in_secs, self.step_dest + str(step_id) + '.xml')            
            self.client.send(data)
            if step_file_name in os.listdir(self.step_dest): # the game has been progressed and the new step information has been saved
                paused = True
                observation = Features(os.path.join(self.step_dest, step_file_name), self.player_side)
                reward = observation.side_.TotalScore
                return TimeStep(step_id, StepType(1), reward, observation)
            time.sleep(0.1) # else, sleep for 0.1 second to give the game a chance to catch up
        # if the game has ended, then save the timestep information with a different step type
        observation = self.get_obs(step_id)
        reward = observation.side_.TotalScore
        return TimeStep(step_id, StepType(2), 0, observation)        

    def get_obs(self, step_id:int) -> Features:
        """
        Description:
            Returns the observation at a particular timestep. This is done by calling the game to export the entire scenario to xml.

        Keyword Arguments:
            step_id: the index of the current step, starting at 0.
        
        Returns:
            (Features) named tuple containing the game observations at the current time index.
        """
        data = "--script \nfile = io.open('{}', 'w')".format(self.step_dest + str(step_id) + '.xml')
        data += "\nio.output(file) \ntheXML = ScenEdit_ExportScenarioToXML() \nio.write(theXML) \nio.close(file)"
        self.client.send(data)
        return Features(os.path.join(self.step_dest, str(step_id) + ".xml"), self.player_side)     

    def reset_connection(self) -> bool:
        """
        Description:
            Restart the client's connection the game.

        Keyword Arguments:
            None

        Returns:
            (bool) connection successful or not
        """
        return self.client.restart()
    
    def check_game_ended(self) -> bool:
        """
        Description:
            Check whether the scenario has ended.
            Reads the recorded txt file in the scenario has ended folder to check for this information.
            The in-game Lua check for this is currently buggy.
        
        Keyword Arguments:
            None

        Returns:
            (bool) whether the game has ended
        """
        data = "--script \nlocal scen = VP_GetScenario() \nif scen.CurrentTimeNum - scen.StartTimeNum >= scen.DurationNum then \nfile = io.open('{}', 'w') \nio.output(file) \nio.write('True') \nio.close(file) \nend".format(self.scen_ended)
        self.client.send(data)
        f = open(self.scen_ended, 'r')
        if f.readline() == 'True':
            return True
        return False
    
    def action_spec(self, observation:Features) -> actions.AvailableFunctions:
        """
        Description:
            Returns the available actions given an observation.
        
        Keyword Arguments:
            observation: the current observations in the game.

        Returns:
            (actions.AvailableFunctions) a list of possible actions
        """        
        return actions.AvailableFunctions(observation)

    def close(self) -> bool:
        """
        Description:
            Close the client connection and the environment.
        
        Keyword Arguments:
            None

        Returns:
            (bool) whether the connection was successfully ended.    
        """
        return self.client.end_connection()
    
class CMOEnv():
    """
    A wrapper that extracts observations from and sends actions to Command: Modern Operations (Steam).
    """
    def __init__(self, 
                 scenario_name:str,
                 player_side: str, 
                 step_size: list, 
                 command_version:str,
                 observation_path: str, 
                 action_path: str,
                 scen_ended_path: str):
        self.client = SteamClient(scenario_name=scenario_name, agent_action_filename=action_path, command_version=command_version) # initialize a client to send data to the game
        if not self.client.connect(): # connect the client to the game
            raise FileNotFoundError("No running instance of Command to connect to.")
        
        self.player_side = player_side # the player's side, this is used to identify units that the player can actually control

        # the step size in h, m, s
        self.h = step_size[0]
        self.m = step_size[1]
        self.s = step_size[2]
        
        self.observation_path = observation_path # the path to the folder containing the xml steps files. These steps files are used to generate observations.
        self.action_path = action_path
        self.scen_ended = scen_ended_path # the path to the text file recording whether or not the scenario has ended. "hacky" way to determine when a scenario ends because the current Lua command for this check is buggy in-game.

        self.current_observation = None
        self.step_id = 0

    def reset(self) -> TimeStep:
        try:
            # with open(self.scen_ended, 'w') as f:
            #     f.write('False') # note in the scenario has ended file that the scenario has ended
            if not self.client.restart_scenario():
                raise ValueError("Client was not able to restart the scenario.")
            
            # reset agent action to nothing
            self.client.send('')
            
            initial_observation = self.get_obs()
            if not initial_observation:
                raise FileNotFoundError("Cannot find observation file to reset the environment.")
            
            self.current_observation = initial_observation
            self.step_id = 0

            return TimeStep(0, StepType(0), 0, initial_observation) # return initial time step
        
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find scen_has_ended.txt.")
    
    def step(self, action=None) -> TimeStep:
        # send the agent's action
        action_written = False
        if action != None:
            action_written = self.client.send(action)

        # step the environment forwards
        if action_written:
            self.client.start_scenario()

        # get the corresponding observation and reward
        # continuously poll the game until the correct time step duration has passed
        new_observation = self.get_obs()
        while new_observation.meta.Time == self.current_observation.meta.Time and not self.check_game_ended():
            time.sleep(0.1)
            new_observation = self.get_obs()

        observation = new_observation
        self.current_observation = new_observation
        reward = observation.side_.TotalScore
        new_timestep = TimeStep(self.step_id, StepType(1), reward, observation)
        self.step_id += 1
        
        return new_timestep

        # if the game has ended, then save the timestep information with a different step type
        # if self.check_game_ended():
        # observation = self.get_obs(step_id)
        # reward = observation.side_.TotalScore
        # return TimeStep(step_id, StepType(2), 0, observation)    

    def get_obs(self) -> FeaturesFromSteam:
        return FeaturesFromSteam(cmo_steam_observation_file_to_xml(self.observation_path), self.player_side) 

    def check_game_ended(self):
        try:
            scenario_ended = cmo_steam_observation_file_to_xml(self.scen_ended)
            if scenario_ended == "true":
                self.client.close_scenario_end_message()
                return True
            return False
        except FileNotFoundError:
            raise FileNotFoundError(f"Cannot find {self.scen_ended}")