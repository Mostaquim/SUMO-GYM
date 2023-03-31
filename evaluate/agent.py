import traci as t
from sumolib import checkBinary
import numpy as np
import config
from modules.appendix import get_lanes, get_links
from modules.action import Action
from modules.phases import PHASES
from modules.evaluate import Evaluator
from modules.reward import RewardCalculator


default_sumoenv_config = {
    'sumo_bin': "sumo-gui",
    'sumo_cfg': "net/freeway.sumocfg",
    'max_timesteps': 3600 * 10,
    'junctions':    [
        {
            'junction': "J1",  # default j3
            'observation_steps': 21,  # default 21
            'lane_obs': 14,  # default 14
            'n_actions': 4,  # default 4
            'vehicle_number': 16  # default 16
        },
        {
            'junction': "J2",  # default j3
            'observation_steps': 21,  # default 21
            'lane_obs': 14,  # default 14
            'n_actions': 4,  # default 4
            'vehicle_number': 16 # default 16
        },
        {
            'junction': "J3",  # default j3
            'observation_steps': 21,  # default 21
            'lane_obs': 14,  # default 14
            'n_actions': 3,  # default 4
            'vehicle_number': 16  # default 16
        },
        # {
        #     'junction': "J4",  # default j3
        #     'observation_steps': 21,  # default 21
        #     'lane_obs': 21,  # default 14
        #     'n_actions': 4,  # default 4
        #     'vehicle_number': 18  # default 16
        # },
        # {
        
        #     'junction': "J5",  # default j3
        #     'observation_steps': 21,  # default 21
        #     'lane_obs': 14,  # default 14
        #     'n_actions': 3,  # default 4
        #     'vehicle_number': 16  # default 16
        # }

    ],


}



class Agent(object):
    def __init__(self, config, evaluator):
        self.binary = checkBinary(config['sumo_bin'])
        self.cfg = config['sumo_cfg']
        self.junctions = config['junctions']
        self.timer = 0
        self.obs_timesteps= []

        
        self.start_sim()
        self.sim = t
        self.lanes = {}
        self.latest_actions = {}
        self.junction_phases = {}
        self.tls_sequences = {}

        self.red_time = 3
        self.yellow_time = 4

        self.action_steps = 10

        self.links = {}
        self.reward_calculator = RewardCalculator(self.sim)
        self.evaluator = evaluator

        self.jun_positions = {}
        self.get_preqs()

        self.reward = 0

    def get_preqs(self):
        for j_obj in self.junctions:
            j = j_obj['junction']
            lane_obs = j_obj['lane_obs']
            observation_steps = j_obj['observation_steps']
            vehicle_number = j_obj['vehicle_number']
  
            
            self.lanes[j] = get_lanes(self.sim, j)

            self.latest_actions[j] = Action(0, -1)

            self.junction_phases[j] = 0
            self.tls_sequences[j] = PHASES[j][0]['primary']

            self.links[j] = get_links(self.sim, j)

            self.jun_positions[j] = np.array(t.junction.getPosition(j.upper()))

            self.obs_timesteps.append(
                np.zeros(shape=(observation_steps, lane_obs, vehicle_number + 2))
            )




    def start_sim(self):
        # t.start([self.binary, "-c", SUMO_CFG, '--start', "--duration-log.disable", "true", "--no-step-log", "true", "--no-warnings", 'true'])
        t.start([self.binary, "-c", self.cfg, '--start'])
        self.sim = t


    def simulationStep(self):
        self.timer += 1
        self.evaluator.step()
        for j_obj in self.junctions:
            j = j_obj['junction']
            tls_type = 'primary' 

            if not self.latest_actions[j].is_done():
                act_time = self.latest_actions[j].timer() 
                if act_time <= self.yellow_time:
                    # yelow light prev phase
                    tls_type = 'yellow'            
                elif act_time - self.yellow_time <= self.red_time:
                    # red light prev phase
                    tls_type = 'red' 
                else:
                    # green light action phase
                    tls_type = 'primary' 
                    self.junction_phases[j] = self.latest_actions[j].action
                    self.latest_actions[j].finish()

            next_sequence = PHASES[j][self.junction_phases[j]][tls_type]

            if next_sequence != self.tls_sequences[j]:
                # TODO switch to next tls light here
                t.trafficlight.setRedYellowGreenState(j, next_sequence )
            self.tls_sequences[j] = next_sequence
        
        t.simulationStep()
        
        for i, j_obj in enumerate(self.junctions):
            lane_obs = j_obj['lane_obs']
            j = j_obj['junction']
            vehicle_num = j_obj['vehicle_number']
            b = np.zeros(shape=(1,lane_obs, vehicle_num + 2))
            b[0] = self.get_single_traffic_light_state(j,lane_obs, vehicle_num)

            self.obs_timesteps[i] = np.concatenate((b, self.obs_timesteps[i][:-1]))


    def get_single_traffic_light_state(self, j, lane_obs,vehicle_num):
        # for p in t.poi.getIDList():
        #     t.poi.remove(p)
        lanes = self.lanes[j]
        pos_array = np.zeros(shape=(lane_obs,vehicle_num))
        
        # tls states
        pl = ''
        tls_arr = []
        z = 0
        states = t.trafficlight.getRedYellowGreenState(j)
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
        
        tls = np.zeros(shape=(lane_obs,2))
        tls[0:len(tls_arr)] = tls_arr
        tls_arr = tls
        

        for i,l in enumerate(self.lanes[j]):
            vehicles = t.lane.getLastStepVehicleIDs(l)[-16:]
            
            for z,v in enumerate(vehicles):
                pos = np.array(t.vehicle.getPosition(v))
                self.reward += self.reward_calculator.calculate_vehicle_reward(v)
                dist = (pos-self.jun_positions[j]) ** 2
                dist = np.sqrt(dist.sum())
                pos_array[i][z] = dist
                w = t.vehicle.getWaitingTime(v)
        return np.concatenate((tls_arr,pos_array),axis=1).astype(float)


    def get_observation(self):
        ret = {}
        for j_obj , o in zip(self.junctions, self.obs_timesteps):
            j = j_obj['junction']
            ret[j] = o.reshape(42,42,-1)
        return ret

    def do_action(self,actions):
        for j in actions:
            if self.latest_actions[j]:
                if self.latest_actions[j].action != actions[j]:
                    self.latest_actions[j] = Action(self.timer, actions[j])
            
        for i in range(self.action_steps):
            self.simulationStep()
            
        


    def step(self, actions):
        obs = self.get_observation()
        self.do_action(actions)
        return obs



