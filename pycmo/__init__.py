from gymnasium.envs.registration import register

register(
     id="FloridistanPycmoGymEnv-v0",
     entry_point="pycmo.env.cmo_gym_env:FloridistanPycmoGymEnv",
)
