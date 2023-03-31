import csv
import imp
from math import tanh
import csv
import numpy as np

class RewardCalculator(object):
    def __init__(self, sim):
        self.sim = sim
        self.accel_store = {}


    def sigmoid(self,x):
        return 1.0 / (1.0 + np.exp(-x))

    def reward_speed(self, x):
        a = 7.38436832
        b = 2.84404085
        x = x *3
        return self.sigmoid(x/a - b)

    def distance_factor(self, x):
        a = 161.35778141
        b = -3.52216987
        return self.sigmoid(x/-a - b)


    def waiting_time(self, x):
        a = 1.0
        b = -11.27617679
        c = 0.66666667
        # return self.sigmoid(x/a + b) / c
        x = x 
        return x/60 

    def deceleration(self, x):
        if x < 0:
            return abs(x/10)
        return 0

    def ttc_factor(self, x):
        if x < 3:
            return 1
        return 0
    def calculate_vehicle_reward(self, vehicle):
        """
        The bread and butter of the agent
        """
        tls = self.sim.vehicle.getNextTLS(vehicle)[0]
        tls_dist = tls[2]
        acceleration = self.sim.vehicle.getAcceleration(vehicle)  
        # jerk = 0
        # if vehicle in self.accel_store:
        #     jerk = (acceleration - self.accel_store[vehicle] ) / 1
        self.accel_store[vehicle] = acceleration
        speed = self.sim.vehicle.getSpeed(vehicle)
        
        waiting_time = self.sim.vehicle.getWaitingTime(vehicle)
        
        ttc = 4

        positive_reward = self.reward_speed(speed) * self.distance_factor(tls_dist)
        
        negative_reward = self.waiting_time(waiting_time) + self.deceleration(acceleration) + self.ttc_factor(ttc)
        
        reward = positive_reward - negative_reward
        
        return reward
