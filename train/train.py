from random import randint
from config import CONFIG
from environment.sumoenv import SumoEnv
from ray.rllib.agents import dqn
import ray
import os
from sys import platform
from ray.tune.logger import pretty_print


class CustomTrain(object):
    def __init__(self, config, checkpoint_path = ''):
        self.config = config
        self.checkpoint_path = checkpoint_path
        self.last_checkpoint = ''
        self.steps = 100

        self.init_trainer()

    
    def init_trainer(self):
        ray.init()
        self.trainer = dqn.DQNTrainer(config=self.config, env=SumoEnv)

        

    
    def iter(self):
        results = self.trainer.train()
        print(pretty_print(results))
        self.last_checkpoint = self.trainer.save()
        

    def training_loop(self):
        for i in range(self.steps):
            try:
                self.iter()
            except :
                pass



ray.init()

trainer = dqn.DQNTrainer(config=CONFIG, env=SumoEnv)



for i in range(10):
    result = trainer.train()
    print(pretty_print(result))
    trainer.save()

