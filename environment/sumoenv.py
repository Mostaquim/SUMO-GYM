
from cmath import exp
import imp
from multiprocessing.connection import wait
from tkinter.messagebox import YES
from pandas import read_table

import gym
from math import tanh
from sumolib import checkBinary
import numpy as np
from random import randint
from modules.evaluate import Evaluator
from modules.action import Action
from uuid import uuid4
from ray.rllib.env.env_context import EnvContext
from modules.phases import get_phases
from modules.appendix import create_cfg, get_lanes, get_links
from modules.reward import RewardCalculator
import os
from sys import platform
import gc
from datetime import datetime

LIBSUMO = False
if platform == "linux" or platform == "linux2":
    os.environ["SUMO_HOME"] = "/home/abid/temp/sumo/"
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "2,3"
    LIBSUMO = True
if LIBSUMO:
    import libsumo as t
else:
    import traci as t

default_sumoenv_config = {
    'sumo_bin' : "sumo",
    'sumo_cfg' : "net/freeway.sumocfg",
    'junction' : "J4", # default j3
    'observation_steps' : 21, # default 21
    'lane_obs' : 21, # default 14
    'n_actions' :4, # default 4
    'max_timesteps' : 5500,
    'evaluate': False,
    'vehicle_number' : 18, # default 16,
    'custom_cfg': False,
    'output_dir': ''
}


class SumoEnv(gym.Env):
    def __init__(self,config: EnvContext):
        # config declaration
        self.config = config
        self.sumo_bin = config['sumo_bin']
        self.binary = checkBinary(self.sumo_bin)
        self.sim_id = uuid4()
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

        self.custom_cfg = config['custom_cfg']

        self.step_called = False

        self.start_sim()

        # store all the lanes and remove duplicates
        self.lanes = get_lanes(self.sim, self.junction)
        # get connected links with tls
        self.links = get_links(self.sim, self.junction)
        # get junction postion later we'll need for distance calculation
        self.jun_pos = np.array(self.sim.junction.getPosition(self.junction))

        # set done == False intially, later if simulation end it will be true
        self.done = False
        # create an empty observation
        self.empty_observation = np.zeros(shape=(self.observation_steps, self.lane_obs,  self.vehicle_number + 2)).reshape(42,42,-1)



        # environment requirements declare spaces, requirement for Rllib/GYM
        self.observation_space = gym.spaces.Box(low=0, high=np.inf, shape=(self.empty_observation.shape))
        self.action_space = gym.spaces.Discrete(self.n_actions)

        # storages and counters 
        self.accel_store = {}
        self.reward_counter = 0
        self.timer = 0
        # obs timestep is the store to store state
        self.observation_store = np.zeros(shape=(self.observation_steps, self.lane_obs, self.vehicle_number + 2))

        

        # traffic light settings 
        
        self.current_phase = 0
        self.red_time = 3
        self.yellow_time = 4
        self.action_steps = 10
        self.PHASES = get_phases(self.junction)
        self.tls_sequence = self.PHASES[self.current_phase ]["primary"]
        self.sim.trafficlight.setRedYellowGreenState(self.junction, self.tls_sequence  )
        self.latest_action = Action(0, -1)
        self.do_action(0)

        self.reward_calculator = RewardCalculator(self.sim)

        self.init_random_steps = True

        self.init_steps = 300


    def generate_cfg(self):
        
        d = self.config['output_dir'] +  datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        return create_cfg(self.config, d)

    def start_sim(self):
        if self.custom_cfg:
            cfg = self.generate_cfg()
            t.start([self.binary, "-c", cfg , '--start'], label=self.sim_id)
            self.sim = t.getConnection(self.sim_id)

        else:
            if LIBSUMO: 
                t.start([self.binary, "-c", self.cfg, '--start', "--duration-log.disable", "true", "--no-step-log", "true", "--no-warnings", 'true'])
                self.sim = t
            else:
                if self.sumo_bin== 'sumo':
                    t.start([self.binary, "-c", self.cfg, '--start', "--duration-log.disable", "true", "--no-step-log", "true", "--no-warnings", 'true']
                    ,label=self.sim_id)
                elif self.sumo_bin== 'sumo-gui':
                    t.start([self.binary, "-c", self.cfg, '--start'], label=self.sim_id)
                self.sim = t.getConnection(self.sim_id)
        self.refresh_stores()
        # if self.evaluate:
        #     self.evaluator = Evaluator(self.sim)


    def refresh_stores(self):
        self.accel_store = {}
        self.observation_store = np.zeros(shape=(self.observation_steps, self.lane_obs, self.vehicle_number + 2))
        self.reward_calculator = RewardCalculator(self.sim)
        gc.collect()


    def reset(self):
        self.done = False
        if self.sim:
            if not LIBSUMO:
                t.switch(self.sim_id)
            t.close()
            self.sim = None
        self.start_sim()
        # advance 300 steps
        self.sim.simulationStep(self.init_steps)
        return np.zeros(shape=(self.observation_steps, self.lane_obs, self.vehicle_number + 2)).reshape(42,42,-1)
    


    def get_observation(self):
        """
        this function called by step function
        """
        return self.observation_store.reshape(42,42,-1)


    def simulation_step(self):
        """
        This function handles every simulation step
        Observations are pushed from here
        This function handles action,state and reward
        """
        self.timer += 1
        tls_type = 'primary' 
        if not self.latest_action.is_done():
            act_time = self.latest_action.timer() 
            if act_time <= self.yellow_time:
                # yelow light prev phase
                tls_type = 'yellow'            
            elif act_time - self.yellow_time <= self.red_time:
                # red light prev phase
                tls_type = 'red' 
            else:
                # green light action phase
                tls_type = 'primary' 
                self.current_phase = self.latest_action.action
                self.latest_action.finish()
        next_sequence = self.PHASES[self.current_phase][tls_type]
        if next_sequence != self.tls_sequence:
            # TODO switch to next tls light here
            self.sim.trafficlight.setRedYellowGreenState(self.junction, next_sequence )
        self.tls_sequence = next_sequence
        self.sim.simulationStep()

        b = np.zeros(shape=(1,self.lane_obs, self.vehicle_number + 2))
        b[0] = self.get_single_traffic_light_state()
        self.observation_store = np.concatenate((b, self.observation_store [:-1]))

        # if self.evaluate:
        #     self.evaluator.step()



    def get_single_traffic_light_state(self):
        """
        Called by: do_action
        This is the core function to create observation
        The output is for a single junciton is 
        [
            TLS STATE, TLS, POS, POS POS
        ]
        reward function is also called from here for each vehicle check single vehicle reward
        """
        # create an empty position array
        pos_array = np.zeros(shape=(self.lane_obs,self.vehicle_number ))
        
        # tls states
        pl = ''
        tls_arr = []
        z = 0
        states = self.sim.trafficlight.getRedYellowGreenState(self.junction)
        # output is a string and replaced by numerical string
        states = states.lower().replace('r','0').replace('y','1').replace('g','2').replace('s','2')
        
        for l in self.links:
            if pl == l[0][0]:
                tls_arr[len(tls_arr)-1][1] = states[z]
                z+=1
            else:
                tls_arr.append([states[z],states[z]])
                z+=1
            pl = l[0][0]
        tls_arr = np.array(tls_arr)
        
        tls = np.zeros(shape=(self.lane_obs,2))
        # since there  should be few empty arrays as the lane_obs >= lane numbers
        tls[0:len(tls_arr)] = tls_arr 
        tls_arr = tls

        
        for i,l in enumerate(self.lanes):
            vehicles = self.sim.lane.getLastStepVehicleIDs(l)[-self.vehicle_number:]
            
            for j,v in enumerate(vehicles):
                # we are only getting postion of each vehicle for observation matrix
                pos = np.array(self.sim.vehicle.getPosition(v))
                dist = (pos-self.jun_pos) ** 2
                dist = np.sqrt(dist.sum())
                pos_array[i][j] = dist

                # here is reward caclulated
                r = self.reward_calculator.calculate_vehicle_reward(v)
                self.reward_counter += r
                # this is to check stats
                # w = self.sim.vehicle.getWaitingTime(v)
                # disp = "r {:.2f} w {:.2f}".format(r,w)
                # self.sim.vehicle.setParameter(v,'diplay' , disp )     
                        
        return np.concatenate((tls_arr,pos_array),axis=1).astype(float)



    def do_action(self,action):
        """
        This function handles actions altogather, called from step()
        Updates the action store 
        and calles simulation step
        """
        if self.latest_action:
            if self.latest_action.action != action:
                self.latest_action = Action(self.timer, action)

        # TODO this loop can be replaced by step(number of steps)
        for i in range(self.action_steps):
            self.simulation_step()


    def step(self,action):
        """
        Called by the agent
        """
        # the simulation steps are taken here
        self.do_action(action)
        
        obs = self.get_observation()
        reward = self.reward_counter
        self.reward_counter = 0
        if self.sim.simulation.getTime() > self.init_steps + self.max_timesteps:
            self.done = True
            # if self.evaluate:
            #     self.evaluator.done()
        info = {}
        return (obs, -1 if self.done else reward,self.done, info)



