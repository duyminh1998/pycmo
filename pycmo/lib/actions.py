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
    pass

  def construct_command(self, functional_call):
    pass