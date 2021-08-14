"""A Command environment."""

from lib import features, protocol
from env.environment import Base, TimeStep, StepType
import time, os

class CMOEnv(Base):
  """A Command environment."""
  def __init__(self, step_dest, step_size):
    self.client = protocol.Client()
    self.client.connect()
    self.step_dest = step_dest
    self.h = step_size[0]
    self.m = step_size[1]
    self.s = step_size[2]

  def reset(self):
      return TimeStep(StepType(0), 0, 0, self.get_obs(self.step_dest, 0))

  def step(self, destination, cur_time, step_id, action=None):
      # send the agent's action
      # self.client.send_action()

      # step the environment forwards
      self.client.send_action("\nVP_RunForTimeAndHalt({Time='" + str(self.h) + ":" + str(self.m) + ":" + str(self.s) + "'})")

      # get the corresponding observation
      paused = False
      dur_in_secs = (int(self.h) * 3600) + (int(self.m) * 60) + int(self.s)
      while not paused:
          data = "--script \nlocal now = ScenEdit_CurrentTime() \nlocal elapsed = now - {} \nif elapsed >= {} then \nfile = io.open('{}' .. '\\\\steps\\\\' .. {} .. '.xml', 'w') \nio.output(file) \ntheXML = ScenEdit_ExportScenarioToXML()\nio.write(theXML) \nio.close(file) \nend".format(cur_time, dur_in_secs, destination, step_id)            
          self.client.send_action(data)
          path = str(step_id) + '.xml'
          if path in os.listdir(os.path.join(destination, "steps")):
              paused = True
              return
          time.sleep(0.1)

  def get_obs(self, destination, step_id):
      data = "--script \nfile = io.open('{}' .. '\\\\steps\\\\' .. {} .. '.xml', 'w') \n".format(destination, step_id)
      data += "io.output(file) \ntheXML = ScenEdit_ExportScenarioToXML()\nio.write(theXML) \nio.close(file)"
      self.client.send_action(data)

  def reset_connection(self):
      try:
          self.client.restart()
      except:
          pass

  def end_game(self):
      try:
          self.client.end_game()
      except:
          pass

  def action_spec(self):
      return super().action_spec()
