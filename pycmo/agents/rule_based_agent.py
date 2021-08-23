# Author: Minh Hua
# Date: 08/21/2021
# Purpose: A rule-based agent for playing the game Command Modern Operations.

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
            self.targets = ['TDDJRS-0HMB0T156BC3O', 'TDDJRS-0HMB0T156BC10', 'TDDJRS-0HMB0T156BC15', 'TDDJRS-0HMB0T156BC16', 'TDDJRS-0HMB0T156BC3Q',
                            'TDDJRS-0HMB0T156BC3P']
            self.current_f15 = 0
            self.f15_status = {}
            for fighter in self.f15s:
                self.f15_status[fighter] = [False, False, False, False, False]

    def get_action(self, observation, VALID_FUNCTIONS):
        if scenario_id[self.scenario] == 10: # wooden leg
            # launch F-15s
            for unit in observation.units:
                if unit.ID == self.f15s[self.current_f15]:
                    if not self.f15_status[unit.ID][0] and int(unit.CA) <= 60:
                        action = VALID_FUNCTIONS[1].corresponding_def(self.player_side, unit.Name, 'true')
                        self.f15_status[unit.ID][0] = True
                        return action
            # refuel
            for unit in observation.units:
                if unit.ID == self.f15s[self.current_f15]:
                    if self.f15_status[unit.ID][0] and not self.f15_status[unit.ID][1]:
                        action = VALID_FUNCTIONS[7].corresponding_def(self.player_side, unit.Name)
                        self.f15_status[unit.ID][1] = True
                        return action
            # strike targets
            for unit in observation.units:
                if unit.ID == self.f15s[self.current_f15]:
                    if self.f15_status[unit.ID][1] and (float(unit.MaxFuel) - float(unit.CurrentFuel)) < 100 and len(observation.contacts) > 1 and observation.contacts[0].ID in self.targets:
                        action = VALID_FUNCTIONS[4].corresponding_def(unit.ID, observation.contacts[0].ID)
                        self.f15_status[unit.ID][2] = True
                        return action
            # refuel

            # rtb
            return VALID_FUNCTIONS[0].corresponding_def()
        else:
            return VALID_FUNCTIONS[0].corresponding_def()
