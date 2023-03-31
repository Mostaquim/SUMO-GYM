import numpy as np
import os

def get_lanes( sim, junction):
    lanes = sim.trafficlight.getControlledLanes(junction)
    # remove lane duplicates
    tmp = []
    for l in lanes:
        if l not in tmp:
            tmp.append(l)
    return tmp


def get_links( sim, junction):
    store = []
    for l in sim.trafficlight.getControlledLinks(junction):
        if l:
            store.append(l)
    return np.array(store)




def create_cfg(config, dir):
    dir = os.path.join('output', dir)
    if not os.path.exists(dir):
        os.makedirs(dir)

    cfg = '<configuration> \
            <input> \
            <net-file value="{}\\net\\export.net.xml"/> \
            <route-files value="{}\\net\\d.rou.xml"/> \
            <additional-files value="map.add.xml"/>\
            </input> \
            <time> \
            <begin value="0"/> \
            <end value="6000"/> \
            </time> \
            <output>\
            <netstate-dump value="out.xml" />\
            <netstate-dump.empty-edges value ="0"/>\
            <queue-output value="que.xml" />\
             </output>\
            </configuration>'.format(
                os.getcwd(),
                os.getcwd(),
                dir,
                dir,
                dir
            )

    additional_file = '<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">\
        <edgeData id="1" freq="900" file="edgedata.xml"/>\
        </additional>\
    '.format(dir)

    f = open("{}\\sumo.sumocfg".format(dir), "w")
    f.write(cfg)
    f.close()

    f = open("{}\\map.add.xml".format(dir), "w")
    f.write(additional_file)
    f.close()

    return "{}\\sumo.sumocfg".format(dir)
