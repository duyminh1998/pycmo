# Author: Minh Hua
# Date: 10/21/2023
# Purpose: A sample agent to interact with the floridistan scenario, demonstrating our ability to work with the Steam version of CMO.
# Scripted agent that will process observations and go through a series of states to strike a target.

from pycmo.agents.base_agent import BaseAgent
from pycmo.lib.features import FeaturesFromSteam, Unit, Contact
from pycmo.lib.actions import AvailableFunctions, launch_aircraft, set_unit_course, auto_attack_contact, rtb

class ScriptedAgent(BaseAgent):
    def __init__(self, player_side:str, attacker_name:str, target_name:str, strike_weapon_name:str):
        super().__init__(player_side)
        self.state = 0
        self.attacker_name = attacker_name
        self.target_name = target_name
        self.strike_weapon_name = strike_weapon_name

    def reset(self) -> None:
        self.state = 0

    def get_unit_info_from_observation(self, features: FeaturesFromSteam, unit_name:str) -> Unit:
        units = features.units
        for unit in units:
            if unit.Name == unit_name:
                return unit
        return None
            
    def get_contact_info_from_observation(self, features: FeaturesFromSteam, contact_name:str) -> Contact:
        contacts = features.contacts
        for contact in contacts:
            if contact.Name == contact_name:
                return contact
        return None

    def action(self, features: FeaturesFromSteam, VALID_FUNCTIONS:AvailableFunctions) -> str:
        action = ""
        attacker = self.get_unit_info_from_observation(features=features, unit_name=self.attacker_name)
        target = self.get_contact_info_from_observation(features=features, contact_name=self.target_name)
        rendez_longitude = -76.9041036640427 # immediate point outside of SAM radius
        rendez_latitude = 28.8515237883916 # immediate point outside of SAM radius

        # in the first state, launch the requested aircraft
        if self.state == 0:
            action = launch_aircraft(side=self.player_side, unit_name=attacker.Name, launch_yn='true')
            self.state += 1

        # in the second state, move aircraft to the intermediate point
        elif self.state == 1 and attacker.CA > 10000:
            action = set_unit_course(side=self.player_side, unit_name=attacker.Name, latitude=rendez_latitude, longitude=rendez_longitude)
            self.state += 1

        # in the third state, make aircraft auto-attack the target
        elif self.state == 2 and attacker.Lon >= -77.5 and target:
            # strike_weapon_name = "GBU-53/B StormBreaker"
            # weapon_max_range = 35
            # print(ScenEdit_GetLoadout( { unitname=attacker.name } ).weapons[3])
            # ScenEdit_AttackContact('Thunder #1', con_guid, {mode='1', weapon=2855, qty=10 })
            action = auto_attack_contact(attacker_id=attacker.ID, contact_id=target.ID) # attack contact automatically
            self.state += 1

        # in the fourth state, move aircraft back to the intermediate point
        elif self.state == 3 and not target:
            action = set_unit_course(side=self.player_side, unit_name=attacker.Name, latitude=rendez_latitude, longitude=rendez_longitude)
            self.state += 1

        # in the fifth state, RTB
        elif self.state == 4 and attacker.Lon <= -76:
            action = rtb(side=self.player_side, unit_name=attacker.Name)
            self.state += 1

        return action
