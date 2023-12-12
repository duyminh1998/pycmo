from pycmo.configs.config import get_config

# open config and set important files and folder paths
config = get_config()

if config["gymnasium"]:
     from gymnasium.envs.registration import register

     register(
          id="FloridistanPycmoGymEnv-v0",
          entry_point="pycmo.env.cmo_gym_env:FloridistanPycmoGymEnv",
     )
