"""A Command environment."""

from lib import features, protocol
from env.environment import Base, TimeStep, StepType
import time, os

class CMOEnv(Base):
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
      f = open(self.scen_ended, 'w')
      f.write('False')
      return TimeStep(0, StepType(0), 0, 0, self.get_obs(self.step_dest, 0))

  def step(self, cur_time, step_id, action=None):
    # send the agent's action
    # self.client.send()

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
      data = "--script \nlocal scen = VP_GetScenario() \nif scen.CurrentTimeNum - scen.StartTimeNum >= scen.DurationNum then \nfile = io.open('{}', 'w') \nio.output(file) \nio.write('True') \nio.close(file) \nend".format(self.scen_ended)
      self.client.send(data)
      f = open(self.scen_ended, 'r')
      if f.readline() == 'True':
          return True
      return False

  def end_game(self):
      try:
          self.client.end_game()
      except:
          pass

  def action_spec(self):
      return super().action_spec()
