from random import randint
from config import CONFIG
from environment.sumoenv import SumoEnv
from ray.rllib.agents import dqn
import ray
import os
from sys import platform
from ray.tune.logger import pretty_print

if platform == "linux" or platform == "linux2":
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "2,3"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    os.environ["OMP_NUM_THREADS"] = "1"



ray.init()

print(CONFIG['env_config'])

trainer = dqn.DQNTrainer(config=CONFIG, env=SumoEnv)


for i in range(500):
    result = trainer.train()
    print(pretty_print(result))
    trainer.save()
