from random import randint

from matplotlib import pyplot as plt
from config import CONFIG
from environment.sumoenv import SumoEnv
from ray.rllib.agents import dqn
import ray
import os
import sys
from ray.tune.logger import pretty_print

from modules.appendix import create_cfg

if sys.platform == "linux" or sys.platform == "linux2":
    os.environ["SUMO_HOME"] = "/home/abid/temp/sumo"
    ray.init(num_cpus=16)
else:
    ray.init()

CONFIG['explore'] = False
CONFIG['env_config']  = {
    'sumo_bin' : "sumo",
    'sumo_cfg' : "net/freeway.sumocfg",
    'junction' : "J4", # default j3
    'observation_steps' : 21, # default 21
    'lane_obs' : 21, # default 14
    'n_actions' :4, # default 4
    'max_timesteps' : 5800,
    'evaluate': False,
    'vehicle_number' : 18, # default 16,
    'custom_cfg' : True,
    'output_dir': 'j4/test'
}


j1_config = CONFIG.copy()

checkpoint_j1 = '.\checkpoint\j1\checkpoint-161'
checkpoint_j2 = '.\checkpoint\j2\checkpoint_000346\checkpoint-346'
checkpoint_j3 = '.\checkpoint\j3\checkpoint_000444\checkpoint-444'
checkpoint_j4 = './checkpoint\j4\checkpoint_000610\checkpoint-610'
checkpoint_j5 = '.\checkpoint\j5\checkpoint_000491\checkpoint-491'

j1_config['env_config']  = {
    'sumo_bin' : "sumo",
    'sumo_cfg' : "net/freeway.sumocfg",
    'junction' : "J1", # default j3
    'observation_steps' : 21, # default 21
    'lane_obs' : 14, # default 14
    'n_actions' :4, # default 4
    'max_timesteps' : 5800,
    'evaluate': False,
    'vehicle_number' : 16, # default 16
    'custom_cfg' : True,
    'output_dir': 'j1\\checkpoint-161'
}

trainer_j1 = dqn.DQNTrainer(config=j1_config, env=SumoEnv)
trainer_j1 = dqn.DQNTrainer(config=j1_config, env=SumoEnv)
trainer_j1.restore(checkpoint_j1)


j2_config = j1_config.copy()
j2_config['env_config']['junction'] = 'J2'
j2_config['env_config']['output_dir'] = 'J2\\346'

trainer_j2 = dqn.DQNTrainer(config=j2_config, env=SumoEnv)
trainer_j2 = dqn.DQNTrainer(config=j2_config, env=SumoEnv)
trainer_j2.restore(checkpoint_j2)

j3_config = j1_config.copy()
j3_config['env_config']['junction'] = 'J3'
j2_config['env_config']['output_dir'] = 'J3\\444'

j3_config['env_config']['n_actions'] = 3


trainer_j3 = dqn.DQNTrainer(config=j3_config, env=SumoEnv)
trainer_j3 = dqn.DQNTrainer(config=j3_config, env=SumoEnv)
trainer_j3.restore(checkpoint_j3)


j5_config = j3_config.copy()
j5_config['env_config']['junction'] = 'J5'
j2_config['env_config']['output_dir'] = 'J5\\491'



trainer_j5 = dqn.DQNTrainer(config=j5_config, env=SumoEnv)
trainer_j5 = dqn.DQNTrainer(config=j5_config, env=SumoEnv)
trainer_j5.restore(checkpoint_j5)



j4_config = CONFIG.copy()

j4_config['env_config'] = {
    'sumo_bin' : "sumo",
    'sumo_cfg' : "net/freeway.sumocfg",
    'junction' : "J4", # default j3
    'observation_steps' : 21, # default 21
    'lane_obs' : 21, # default 14
    'n_actions' :4, # default 4
    'max_timesteps' : 5800,
    'evaluate': False,
    'vehicle_number' : 18, # default 16
    'custom_cfg' : True,
    'output_dir': 'j4\\610'
}



trainer_j4 = dqn.DQNTrainer(config=j4_config, env=SumoEnv)
trainer_j4 = dqn.DQNTrainer(config=j4_config, env=SumoEnv)
trainer_j4.restore(checkpoint_j4)



trainer_j1.train()
trainer_j2.train()
trainer_j3.train()
trainer_j4.train()
trainer_j5.train()