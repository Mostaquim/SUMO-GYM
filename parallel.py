from tabnanny import check
from evaluate.agent import Agent, default_sumoenv_config
from config import CONFIG
from environment.emptyenv import EmptyEnv
from ray.rllib.agents import dqn
import ray
import traci as t

from modules.evaluate import Evaluator


checkpoint_j1 = '.\checkpoint\j1\checkpoint-161'
checkpoint_j2 = '.\checkpoint\j2\checkpoint_000346\checkpoint-346'
checkpoint_j3 = '.\checkpoint\j3\checkpoint_000444\checkpoint-444'
checkpoint_j4 = './checkpoint\j4\checkpoint_000610\checkpoint-610'
checkpoint_j5 = '.\checkpoint\j5\checkpoint_000491\checkpoint-491'

ray.init()


CONFIG['explore'] = False
CONFIG['num_gpus_per_worker'] = 0
CONFIG['num_gpus'] = 0

j1_config = CONFIG.copy()

j1_config['env_config']  = {
    'sumo_bin' : "sumo",
    'sumo_cfg' : "net/freeway.sumocfg",
    'junction' : "J1", # default j3
    'observation_steps' : 21, # default 21
    'lane_obs' : 14, # default 14
    'n_actions' :4, # default 4
    'max_timesteps' : 5800,
    'evaluate': False,
    'vehicle_number' : 16 # default 16
}

trainer_j1 = dqn.DQNTrainer(config=j1_config, env=EmptyEnv)
trainer_j1 = dqn.DQNTrainer(config=j1_config, env=EmptyEnv)
trainer_j1.restore(checkpoint_j1)


j2_config = j1_config.copy()
j2_config['env_config']['junction'] = 'J2'

trainer_j2 = dqn.DQNTrainer(config=j2_config, env=EmptyEnv)
trainer_j2 = dqn.DQNTrainer(config=j2_config, env=EmptyEnv)
trainer_j2.restore(checkpoint_j2)

j3_config = j1_config.copy()
j3_config['env_config']['junction'] = 'J3'
j3_config['env_config']['n_actions'] = 3


trainer_j3 = dqn.DQNTrainer(config=j3_config, env=EmptyEnv)
trainer_j3 = dqn.DQNTrainer(config=j3_config, env=EmptyEnv)
trainer_j3.restore(checkpoint_j3)


j5_config = j3_config.copy()
j5_config['env_config']['junction'] = 'J5'



# trainer_j5 = dqn.DQNTrainer(config=j5_config, env=EmptyEnv)
# trainer_j5 = dqn.DQNTrainer(config=j5_config, env=EmptyEnv)
# trainer_j5.restore(checkpoint_j5)



# j4_config = CONFIG.copy()

# j4_config['env_config'] = {
#     'sumo_bin' : "sumo",
#     'sumo_cfg' : "net/freeway.sumocfg",
#     'junction' : "J4", # default j3
#     'observation_steps' : 21, # default 21
#     'lane_obs' : 21, # default 14
#     'n_actions' :4, # default 4
#     'max_timesteps' : 5800,
#     'evaluate': False,
#     'vehicle_number' : 18 # default 16
# }



# trainer_j4 = dqn.DQNTrainer(config=j4_config, env=EmptyEnv)
# trainer_j4 = dqn.DQNTrainer(config=j4_config, env=EmptyEnv)
# trainer_j4.restore(checkpoint_j4)





evaluator = Evaluator(t)


agent = Agent(config=default_sumoenv_config, evaluator=evaluator)

actions = {
    'J1': 1,
    'J2': 1,
    'J3': 1,
    # 'J4': 1,
    # 'J5': 1,
}

obs = agent.step(actions=actions)


for i in range(360*5):

    a1 = trainer_j1.compute_single_action(obs['J1'], explore=False)
    a2 = trainer_j2.compute_single_action(obs['J2'], explore=False)
    a3 = trainer_j3.compute_single_action(obs['J3'], explore=False)
    # a4 = trainer_j4.compute_single_action(obs['J4'], explore=False)
    # a5 = trainer_j5.compute_single_action(obs['J5'], explore=False)

    actions = {
        # 'J1' : a1 ,
        # 'J2' : a2 
        'J3' : a3 ,
        # 'J4' : a4 ,
        # 'J5' : a5 
    }

    print(actions)
    obs = agent.step(actions)


print(agent.reward)
evaluator.done()

# for i in range(100):
#     r = a.step(actions)
#     print(r)