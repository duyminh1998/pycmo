# Author: Minh Hua
# Date: 08/28/2021
# Purpose: A scripted agent for playing the game Command Modern Operations.

scenario_id = {
    'brass_drum': 0,
    'english_jets_over_uganda': 1,
    'fighter_weapons_school': 2,
    'iron_hand': 3,
    'khark': 4,
    'north_pacific_shootout': 5,
    'pyrpolitis': 6,
    'sea_of_fire': 7,
    'shamal': 8,
    'task_force_normandy': 9,
    'wooden_leg': 10,
    'none': 11
}

class ScriptedAgent():
    def __init__(self, scenario, player_side):
        """An agent that follows a scripted set of actions according to the chosen scenario, regardless of observation."""
        self.scenario = scenario
        self.player_side = player_side
        if scenario_id[self.scenario] == 10:
            self.assigned_f15_to_missions = False
            self.refueled = []

    def get_action(self, observation, VALID_FUNCTIONS):
        if scenario_id[self.scenario] == 10: # wooden leg
            if not self.assigned_f15_to_missions and len(observation.contacts) > 0:
                # assign initial strike missions
                targets = "{"
                for contact in observation.contacts:
                    if contact.Name.split(" ")[0] == "[Target]":
                        targets += "\'" + contact.ID + "\'" + ", "
                targets = targets[:-2] + "}"
                action = "--script \nTool_EmulateNoConsole(true)"
                action += "\nScenEdit_AddMission('Israel', 'Strike', 'strike', {type='land'})"
                #action += "\nScenEdit_SetMission('Israel','Strike',{StrikeFlightSize=1})"
                action += "\nScenEdit_AssignUnitAsTarget({}, 'Strike')".format(targets)
                for unit in observation.units:
                    if unit.Name.split(" ")[0] == "106":
                        action += "\nScenEdit_AssignUnitToMission('{}','Strike')".format(unit.Name)
                self.assigned_f15_to_missions = True
                return action
            else:
                # refuel if unit has less than half its fuel
                for unit in observation.units:
                    if unit.Name.split(" ")[0] == "106":
                        if unit.CurrentFuel < (unit.MaxFuel * 0.9) and unit.Name not in self.refueled:
                            action = VALID_FUNCTIONS[7].corresponding_def(self.player_side, unit.Name)
                            self.refueled.append(unit.Name)
                            return action
            return VALID_FUNCTIONS[0].corresponding_def()
        else:
            return VALID_FUNCTIONS[0].corresponding_def()            