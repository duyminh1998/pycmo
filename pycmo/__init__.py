from gymnasium.envs.registration import register

register(
     id="CMOGymEnv-v0",
     entry_point="pycmo.env.cmo_env:CMOGymEnv",
)
