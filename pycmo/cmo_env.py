"""A Command environment."""

from lib import features, protocol
from env import environment
import time, os

class CMOEnv(environment.Base):
  """A Command environment."""
  def __init__(self):
    self.client = protocol.Client()
    self.client.connect()
    # self.states = [init_ts]

  def get_ts(self, ts):
    pass
    #return self.states[ts]

  def step(self, h, m, s):
      self.client.send_action("VP_RunForTimeAndHalt({Time='" + str(h) + ":" + str(m) + ":" + str(s) + "'})")

  def step_and_get_obs(self, h, m, s, destination, cur_time, step_id):
      self.client.send_action("\nVP_RunForTimeAndHalt({Time='" + str(h) + ":" + str(m) + ":" + str(s) + "'})")
      paused = False
      dur_in_secs = (int(h) * 3600) + (int(m) * 60) + int(s)
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

  def reset(self):
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
