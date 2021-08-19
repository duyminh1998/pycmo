# Author: Minh Hua
# Date: 08/16/2021
# Purpose: A Command environment.

# imports
from pycmo.lib import features, protocol, actions
import collections, enum
import time, os

class TimeStep(collections.namedtuple(
    'TimeStep', ['step_id', 'step_type', 'reward', 'discount', 'observation'])):
  """Returned with every call to `step` and `reset` on an environment.

  A `TimeStep` contains the data emitted by an environment at each step of
  interaction. A `TimeStep` holds a `step_type`, an `observation`, and an
  associated `reward` and `discount`.

  The first `TimeStep` in a sequence will have `StepType.FIRST`. The final
  `TimeStep` will have `StepType.LAST`. All other `TimeStep`s in a sequence will
  have `StepType.MID.

  Author: DeepMind

  Attributes:
    step_id: A scalar that represents the ID of a step
    step_type: A `StepType` enum value.
    reward: A scalar, or 0 if `step_type` is `StepType.FIRST`, i.e. at the
      start of a sequence.
    discount: A discount value in the range `[0, 1]`, or 0 if `step_type`
      is `StepType.FIRST`, i.e. at the start of a sequence.
    observation: A NumPy array, or a dict, list or tuple of arrays.
  """
  def first(self):
    return self.step_type is StepType.FIRST

  def mid(self):
    return self.step_type is StepType.MID

  def last(self):
    return self.step_type is StepType.LAST


class StepType(enum.IntEnum):
  """Defines the status of a `TimeStep` within a sequence.
  Author: DeepMind
  """
  # Denotes the first `TimeStep` in a sequence.
  FIRST = 0
  # Denotes any `TimeStep` in a sequence that is not FIRST or LAST.
  MID = 1
  # Denotes the last `TimeStep` in a sequence.
  LAST = 2

class CMOEnv():
  def __init__(self, step_dest: str, step_size: list, player_side: str, scen_ended_path: str):
    """A Command environment.

    Args:
      step_dest: the path of folder to hold the steps
      step_size: a list containing the step size in the format ["h", "m", "s"]
      player_side: the string identifying the player's side. Side should exist in the game
      scen_ended_path: the path to the text file that records whether a scenario has ended or not
    """
    self.client = protocol.Client() # initialize a client to send data to the game
    self.client.connect() # connect the client to the game
    self.player_side = player_side # the player's side
    self.step_dest = step_dest # the path to the folder containing the xml steps files
    self.scen_ended = scen_ended_path # the path to the text file recording whether or not the scenario has ended
    # the step size in h, m, s
    self.h = step_size[0]
    self.m = step_size[1]
    self.s = step_size[2]

  def reset(self):
    """Starts a new sequence and returns the first `TimeStep` of this sequence.

    Returns:
      A `TimeStep` namedtuple containing:
        step_ind: 
        step_type: A `StepType` of `FIRST`.
        reward: Zero.
        discount: Zero.
        observation: 
    """
    f = open(self.scen_ended, 'w')
    f.write('False')
    return TimeStep(0, StepType(0), 0, 0, self.get_obs(0))

  def step(self, cur_time, step_id, action=None):
    """Updates the environment according to the action and returns a `TimeStep`.

    If the environment returned a `TimeStep` with `StepType.LAST` at the
    previous step, this call to `step` will start a new sequence and `action`
    will be ignored.

    This method will also start a new sequence if called after the environment
    has been constructed and `restart` has not been called. Again, in this case
    `action` will be ignored.

    Args:
      cur_time: the current time
      step_id: the current step ID
      action: a string containing the Lua script to send to the environment

    Returns:
      A `TimeStep` namedtuple containing:
        step_id: 
        step_type: A `StepType` value.
        reward: Reward at this timestep.
        discount: A discount in the range [0, 1].
        observation:
    """      
    # send the agent's action
    if action != None:
        self.client.send(action)

    # step the environment forwards
    self.client.send("\nVP_RunForTimeAndHalt({Time='" + str(self.h) + ":" + str(self.m) + ":" + str(self.s) + "'})")

    # get the corresponding observation, reward and discount
    paused = False
    dur_in_secs = (int(self.h) * 3600) + (int(self.m) * 60) + int(self.s)
    step_file_name = str(step_id) + '.xml'
    while not (paused or self.check_game_ended()):
        data = "--script \nlocal now = ScenEdit_CurrentTime() \nlocal elapsed = now - {} \nif elapsed >= {} then \nfile = io.open('{}', 'w') \nio.output(file) \ntheXML = ScenEdit_ExportScenarioToXML()\nio.write(theXML) \nio.close(file) \nend".format(cur_time, dur_in_secs, self.step_dest + str(step_id) + '.xml')            
        self.client.send(data)
        if step_file_name in os.listdir(self.step_dest):
            paused = True
            observation = features.Features(os.path.join(self.step_dest, step_file_name), self.player_side)
            reward = observation.side_.TotalScore
            discount = 0
            return TimeStep(step_id, StepType(1), reward, discount, observation)
        time.sleep(0.1)
    observation = self.get_obs(step_id)
    reward = observation.side_.TotalScore
    discount = 0    
    return TimeStep(step_id, StepType(2), 0, 0, observation)

  def get_obs(self, step_id):
      """Returns the observation at a particular timestep"""
      data = "--script \nfile = io.open('{}', 'w') \n".format(self.step_dest + str(step_id) + '.xml')
      data += "io.output(file) \ntheXML = ScenEdit_ExportScenarioToXML()\nio.write(theXML) \nio.close(file)"
      self.client.send(data)
      return features.Features(os.path.join(self.step_dest, str(step_id) + ".xml"), self.player_side)
    
  def get_timestep(self, step_id):
    observation = self.get_obs(step_id)
    reward = observation.side_.TotalScore
    discount = 0
    return TimeStep(step_id, StepType(1), reward, discount, observation)

  def reset_connection(self):
    """Reset the client connection"""
    self.client.restart()
  
  def check_game_ended(self):
      """Check whether the scenario has ended"""
      data = "--script \nlocal scen = VP_GetScenario() \nif scen.CurrentTimeNum - scen.StartTimeNum >= scen.DurationNum then \nfile = io.open('{}', 'w') \nio.output(file) \nio.write('True') \nio.close(file) \nend".format(self.scen_ended)
      self.client.send(data)
      f = open(self.scen_ended, 'r')
      if f.readline() == 'True':
          return True
      return False

  def close(self):
    """Close the client connection and the environment"""
    self.client.end_connection()

  def action_spec(self, observation):
      """Returns the available actions given an observation"""
      return actions.AvailableFunctions(observation)

  def __enter__(self):
    """Allows the environment to be used in a with-statement context."""
    return self

  def __exit__(self, unused_exception_type, unused_exc_value, unused_traceback):
    """Allows the environment to be used in a with-statement context."""
    self.close()

  def __del__(self):
    self.close()