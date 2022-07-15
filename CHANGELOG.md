<a name="1.0.0"></a>
# 1.0.0 (2022-07-15)
- This project is on hold for the time being as I lost access to the Premium license for Command Modern Operations.

<a name="1.0.0"></a>
# 1.0.0 (2022-06-21)
- Implementing a Q-learning agent to navigate an aircraft through a "track".
    - Discretized the space into a grid of discrete coordinates. A related problem is to figure out the appropriate time step size.
    - Discretization strategy involves replacing the aircraft's actual coordinates with the closest coordinate on the grid. This way, the Q-table is still discrete.
    - Modified Q-learning agent to be compatible with this problem set up.
    - Available actions and state space are the same, i.e. the set of coordinates on the grid.
    - Figuring out how to restart the game after a training epoch is complete.

<a name="1.0.0"></a>
# 1.0.0 (2022-06-15)
- Improved code documentation.
- Removed discounts from the TimeStep object that gets returned at every time step, because discount is a parameter that is dependent on the agent and not the environment.
- Implementing a Q-learning agent to navigate an aircraft through a "track".

<a name="1.0.0"></a>
# 1.0.0 (2021-08-15)
- Project creation.
