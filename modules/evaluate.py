from datetime import datetime
from time import strftime
import numpy as np
import pandas as pd

class Evaluator(object):
    def __init__(self,sim):
        self.sim = sim
        self.lanes = None
        self.stats = None
        

    def step(self):
        if self.lanes == None:
            self.lanes = self.sim.lane.getIDList()
            self.stats = Statistics(self.lanes)
        
        for l in self.lanes:
            if ':' not in l:
                wt      =   self.sim.lane.getWaitingTime(l)
                speed   =   self.sim.lane.getLastStepMeanSpeed(l)
                travel  =   self.sim.lane.getTraveltime(l)
                count   =   self.sim.lane.getLastStepVehicleNumber(l)
                self.stats.update_lane_stats(l,wt, speed, travel, count)
        self.stats.step()
    
    def done(self):
        self.stats.save()


class Statistics(object):
    def __init__(self,lanes):
        self.data = {}
        self.step_count = 0
        for l in lanes:
            if ':' not in l:
                self.data[l] = [0,0,0,0,0]
        self.file_name = "./stats/" + datetime.now().strftime("%m_%d_%Y_%H_%M_%S") + '.csv'

    def update_lane_stats(self, lane_id, waiting_time, mean_speed, travel_time, count):
    
        self.data[lane_id][0] += waiting_time
        self.data[lane_id][1] += mean_speed
        self.data[lane_id][2] += travel_time
        self.data[lane_id][3] += count
        self.data[lane_id][4] = self.step_count

        return self

    def step(self):
        self.step_count +=1

   
    def save(self):
        df = pd.DataFrame(self.data)
        df = df.T
        df = df.rename({
             0: 'Waiting Time', 
             1: 'Mean Speed', 
             2: 'Travel_time',
             3: 'Count',
             4: 'Step'
             }, axis='columns')
        df.to_csv(self.file_name)