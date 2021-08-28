# Author: Minh Hua
# Date: 08/28/2021
# Purpose: A scripted agent for playing the game Command Modern Operations.

scenario_id = {
    'Operation Brass Drum, 2017': 0,
    '2 - English Jets over Uganda, 1973': 1,
    'Fighter Weapons School - GAT 5 and 6, 1977': 2,
    'Iron Hand, 2014': 3,
    'Khark Island Raid, 1985': 4,
    'North Pacific Shootout, 1989': 5,
    'Pyrpolitis 1-14, 2014': 6,
    'Sea of Fire, 1982': 7,
    'Shamal, 1991': 8,
    'Task Force Normandy, 1991': 9,
    'Wooden Leg, 1985': 10,
    'None': 11
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