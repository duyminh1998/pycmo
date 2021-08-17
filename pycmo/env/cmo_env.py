"""A Command environment."""

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
  """Defines the status of a `TimeStep` within a sequence."""
  # Denotes the first `TimeStep` in a sequence.
  FIRST = 0
  # Denotes any `TimeStep` in a sequence that is not FIRST or LAST.
  MID = 1
  # Denotes the last `TimeStep` in a sequence.
  LAST = 2

class CMOEnv():
  """A Command environment."""
  def __init__(self, step_dest, step_size, player_side, scen_ended_path):
    self.client = protocol.Client()
    self.client.connect()
    self.player_side = player_side
    self.step_dest = step_dest
    self.scen_ended = scen_ended_path
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
    return TimeStep(0, StepType(0), 0, 0, self.get_obs(self.step_dest, 0))

  def step(self, cur_time, step_id, action=None):
    """Updates the environment according to the action and returns a `TimeStep`.

    If the environment returned a `TimeStep` with `StepType.LAST` at the
    previous step, this call to `step` will start a new sequence and `action`
    will be ignored.

    This method will also start a new sequence if called after the environment
    has been constructed and `restart` has not been called. Again, in this case
    `action` will be ignored.

    Args:
      action: A NumPy array, or a dict, list or tuple of arrays corresponding to
        `action_spec()`.

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
    path = str(step_id) + '.xml'
    while not (paused or self.check_game_ended()):
        data = "--script \nlocal now = ScenEdit_CurrentTime() \nlocal elapsed = now - {} \nif elapsed >= {} then \nfile = io.open('{}' .. '\\\\steps\\\\' .. {} .. '.xml', 'w') \nio.output(file) \ntheXML = ScenEdit_ExportScenarioToXML()\nio.write(theXML) \nio.close(file) \nend".format(cur_time, dur_in_secs, self.step_dest, step_id)            
        self.client.send(data)
        if path in os.listdir(os.path.join(self.step_dest, "steps")):
            paused = True
            observation = features.Features(os.path.join(self.step_dest, "steps", path), self.player_side)
            reward = 0
            discount = 0
            return TimeStep(step_id, StepType(1), reward, discount, observation)
        time.sleep(0.1)
    return TimeStep(step_id, StepType(2), 0, 0, self.get_obs(self.step_dest, step_id))

  def get_obs(self, destination, step_id):
      """Returns the observation at a particular timestep"""
      data = "--script \nfile = io.open('{}' .. '\\\\steps\\\\' .. {} .. '.xml', 'w') \n".format(destination, step_id)
      data += "io.output(file) \ntheXML = ScenEdit_ExportScenarioToXML()\nio.write(theXML) \nio.close(file)"
      self.client.send(data)
      return features.Features(os.path.join(self.step_dest, "steps", str(step_id) + ".xml"), self.player_side)

  def reset_connection(self):
      try:
          self.client.restart()
      except:
          pass
  
  def check_game_ended(self):
      """Check whether the scenario has ended"""
      data = "--script \nlocal scen = VP_GetScenario() \nif scen.CurrentTimeNum - scen.StartTimeNum >= scen.DurationNum then \nfile = io.open('{}', 'w') \nio.output(file) \nio.write('True') \nio.close(file) \nend".format(self.scen_ended)
      self.client.send(data)
      f = open(self.scen_ended, 'r')
      if f.readline() == 'True':
          return True
      return False

  def close(self):
      try:
          self.client.end_game()
      except:
          pass

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