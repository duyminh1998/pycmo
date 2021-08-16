import collections

# pylint: disable=line-too-long
available_functions = ["no_op", "ScenEdit_AddMission", "ScenEdit_AddReferencePoint", "ScenEdit_AssignUnitAsTarget", 
"ScenEdit_AssignUnitToMission", "ScenEdit_AttackContact", "ScenEdit_DeleteMission", "ScenEdit_DeleteReferencePoint",
"ScenEdit_RefuelUnit", "ScenEdit_RemoveUnitAsTarget", "ScenEdit_SetEMCON", "ScenEdit_SetLoadout", "ScenEdit_SetMission",
"ScenEdit_SetReferencePoint", "ScenEdit_SetUnit"]

def no_op():
  return ""

def ScenEdit_SetUnit():
  pass

class ArgumentType():
  pass

class Function(collections.namedtuple(
  "Function", ['id', 'name', 'function_type', 'args'])):

  @classmethod
  def no_op(cls, id, name, function_type):
    return cls(id, name, FUNCTION_TYPES(function_type))

FUNCTION_TYPES = {
  no_op: [],
  ScenEdit_SetUnit: []
}

_FUNCTIONS = [
  Function.no_op(0, "no_op", no_op)
]

class FunctionCall(collections.namedtuple(
    "FunctionCall", ["function", "arguments"])):
  """Represents a function call action.

  Attributes:
    function: Store the function id, eg 2 for select_point.
    arguments: The list of arguments for that function, each being a list of
        ints. For select_point this could be: [[0], [23, 38]].
  """
  def __init__(self):
    pass

  def construct_command(self, functional_call):
    pass