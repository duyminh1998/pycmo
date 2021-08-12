"""A Command environment."""

from pycmo.lib import features, protocol
from pycmo.env import environment

class CMOEnv(environment.Base):
  """A Command environment."""
  def __init__(self, init_ts):
    self.client = protocol.Client()
    self.states = [init_ts]

  def get_ts(self, ts):
    return self.states[ts]

  def step(self, action):
    pass