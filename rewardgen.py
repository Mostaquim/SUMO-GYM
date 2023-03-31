import traci as t
from sumolib import checkBinary
import itertools
from modules.appendix import get_lanes
from modules.reward import RewardCalculator
from modules.evaluate import Evaluator, Statistics


binary = checkBinary('sumo-gui')


t.start([binary, "-c", 'net/fourways.sumocfg', '--start', '--quit-on-end', 'true'])

# d = ['NJ', 'SJ', 'WJ', "EJ"]
# e = ['JN', 'JS', 'JW', "JE"]
evaluator = Evaluator(t)

d = ['NJ', 'WJ' ]
e = ['JS','JE']
i = 0
rc = RewardCalculator(t)
routes = []
for subset in itertools.product(d, e):
    no_j = [n.replace('J', '') for n in subset]
    if no_j[0] == no_j[1]:
        continue
    print(subset)
    route = "route{}".format(i)
    routes.append(route)
    r = t.route.add(route, list(subset))
    i += 1

v = 0

lanes = get_lanes(t, 'J')
steps = 100

t.vehicle.add("car{}".format(v), routes[3])
v+= 1
t.vehicle.add("car{}".format(v), routes[3])
v+= 1

for i in range(steps):
    t.trafficlight.setRedYellowGreenState('J','rrrrGGGGGGGGGGGG' )

    t.simulationStep()
    reward_counter = 0
        
    t.vehicle.add("car{}".format(v), routes[0])
    v+= 1

    evaluator.step()
    for l in lanes:
        vehicles = t.lane.getLastStepVehicleIDs(l)[-16:]
        

        for vehicle in list(vehicles):
            reward = rc.calculate_vehicle_reward(vehicle)
            reward_counter += reward

    print(reward_counter)


evaluator.done()





