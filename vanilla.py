import traci as t
from sumolib import checkBinary
import itertools
from modules.appendix import get_lanes
from modules.reward import RewardCalculator
from modules.evaluate import Evaluator, Statistics
import numpy as np
import json

binary = checkBinary('sumo')


t.start([binary, "-c", 'net/freeway.sumocfg', '--start', '--quit-on-end', 'true'])

# d = ['NJ', 'SJ', 'WJ', "EJ"]
# e = ['JN', 'JS', 'JW', "JE"]
evaluator = Evaluator(t)

steps = 5810

for i in range(steps):
    t.simulationStep()
#     evaluator.step()
# evaluator.done()


# junctions = ['J1','J2','J3','J4','J5']



# arr = {}
# for j in junctions:
#     lanes = get_lanes(t, j)

#     arr[j] = lanes
        

# j = json.dumps(arr)

# print(j)