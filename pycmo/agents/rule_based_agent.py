# Author: Minh Hua
# Date: 08/21/2021
# Purpose: A rule-based agent for playing the game Command Modern Operations.

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

class RuleBasedAgent():
    def __init__(self, scenario, player_side):
        self.scenario = scenario
        self.player_side = player_side
        if scenario_id[self.scenario] == 10: # wooden leg
            self.tankers = ['c399336f-1b14-41b8-95fa-fcacd7066114', '5c29fd4d-432a-4ad9-974f-b1beffa292e2']
            self.f15s = ['189891cb-79e9-4282-9942-bc2b2cff6b79',
                    '137faf9f-3f90-435f-bbc7-477f6112538d',
                    '2854a5bf-bbfd-4a71-ab1e-ddab9c8b0f09',
                    '864614a3-d3ec-4277-89c4-3da824853959',
                    '882e5742-2e6c-42e9-b255-f94fdd9fd7dd',
                    '93af9284-7182-4d05-afd1-8b2242f2f558',
                    '3e5abbac-f3bf-4f52-8c12-8b3519b801c0',
                    'dbbf1f2f-cdf7-4379-83ae-a8f1e3311621',
                    'f4e92c78-b6ab-4634-a034-2445b8e830af',
                    '421f05aa-d3f8-4cd2-bac7-adac542a5cf6']
            self.targets_assigned_f15 = {}
            self.current_f15 = 0
            self.f15_status = {}
            for fighter in self.f15s:
                self.f15_status[fighter] = [False, False]

    def get_action(self, observation, VALID_FUNCTIONS):
        if scenario_id[self.scenario] == 10: # wooden leg
            try:
                # launch F-15s
                for unit in observation.units:
                    if unit.ID == self.f15s[self.current_f15]:
                        if not self.f15_status[unit.ID][0]:
                            action = VALID_FUNCTIONS[1].corresponding_def(self.player_side, unit.Name, 'true')
                            self.f15_status[unit.ID][0] = True
                            return action

                # strike targets
                for unit in observation.units:
                    if unit.ID == self.f15s[self.current_f15]:
                        if self.f15_status[unit.ID][0] and not self.f15_status[unit.ID][1]:
                            for contact in observation.contacts:
                                if contact.Name.split(" ")[0] == "[Target]" and contact.Name not in self.targets_assigned_f15.keys():
                                    action = VALID_FUNCTIONS[4].corresponding_def(unit.ID, contact.ID)
                                    self.f15_status[unit.ID][1] = True
                                    self.targets_assigned_f15[contact.Name] = unit.ID
                                    return action
                
                # check if striked
                for unit in observation.units:
                    if unit.ID == self.f15s[self.current_f15] and self.f15_status[unit.ID][1]:
                        for mount in unit.Mounts:
                            for unit_weapon in mount.Weapons:
                                if unit_weapon.QuantRemaining < unit_weapon.MaxQuant:
                                    for target, striker in zip(self.targets_assigned_f15.keys(), self.targets_assigned_f15.values()):
                                        if striker == unit.ID:
                                            del self.targets_assigned_f15[target]
                                            break
                                    self.current_f15 += 1
                                    return VALID_FUNCTIONS[0].corresponding_def()
                        for unit_weapon in unit.Loadout.Weapons:
                            if unit_weapon.QuantRemaining < unit_weapon.MaxQuant:
                                for target, striker in zip(self.targets_assigned_f15.keys(), self.targets_assigned_f15.values()):
                                    if striker == unit.ID:
                                        del self.targets_assigned_f15[target]
                                        break
                                self.current_f15 += 1
                                return VALID_FUNCTIONS[0].corresponding_def()               
                return VALID_FUNCTIONS[0].corresponding_def()
            except:
                return VALID_FUNCTIONS[0].corresponding_def()
        else:
            return VALID_FUNCTIONS[0].corresponding_def()
