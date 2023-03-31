from sumolib import checkBinary
import numpy as np
import gym
from ray.rllib.env.env_context import EnvContext


class EmptyEnv(gym.Env):
    def __init__(self,config: EnvContext):
        # config declaration
        self.sumo_bin = config['sumo_bin']
        self.binary = checkBinary(self.sumo_bin)
        self.cfg = config['sumo_cfg']
        # name of the junction make sure junciton name and tls name is same
        self.junction = config['junction']
        
        # number of observation steps to process in a single state
        self.observation_steps = config['observation_steps']
        # number of lanes to put in observation
        self.lane_obs = config['lane_obs']
        # number of action/phases
        self.n_actions = config['n_actions']

        self.max_timesteps = config['max_timesteps']

        self.evaluate = config['evaluate']

        self.vehicle_number = config['vehicle_number']
        

        self.third_dim =int( self.observation_steps * self.lane_obs  * (self.vehicle_number + 2) / (42*42))
        print(self.third_dim)
        # declare the lanes here
        # remove lane duplicates
        self.done = False

        # TODO change links here
        
        # gym prequisites
        self.observation = self.reset()
        self.action_space = gym.spaces.Discrete(self.n_actions)

        # TODO need to rethink shapes
        self.observation_space = gym.spaces.Box(low=0, high=np.inf, shape=(42,42,self.third_dim))
        
        
    def reset(self):
        return np.zeros((42,42,self.third_dim))
    
    def step(self,action):
        obs = np.zeros((42,42,self.third_dim))
        return (obs, -1 if self.done else 0,self.done, {}) 


class EmptyEnvThree(EmptyEnv):
    def __init__(self, env_config):
        super().__init__(env_config)
        self.action_space = gym.spaces.Discrete(3)