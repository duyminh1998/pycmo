import collections

class FunctionCall(collections.namedtuple(
    "FunctionCall", ["function", "arguments"])):
  """Represents a function call action.

  Attributes:
    function: Store the function id, eg 2 for select_point.
    arguments: The list of arguments for that function, each being a list of
        ints. For select_point this could be: [[0], [23, 38]].
  """
  def __init__(self):
    available_functions = ["ScenEdit_AssignUnitAsTarget", "ScenEdit_AssignUnitToMission", 
    "ScenEdit_AttackContact", "ScenEdit_HostUnitToParent", "ScenEdit_SetDoctrine", "ScenEdit_SetUnit", 
    "ScenEdit_TransferCargo", "ScenEdit_UnloadCargo"]
    pass

  def construct_command(self, functional_call):
    pass

class Function():
  def __init__(self):
    pass

class Wrapper():
  def __init__(self):
    pass

class Selector():
  def __init__(self):
    pass

class Table():
  def __init__(self):
    pass