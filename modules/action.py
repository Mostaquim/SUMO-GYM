class Action(object):
    def __init__(self, time, action) -> None:
        self.time = time
        self.action = action
        self.done = False
        self.time = 0
    
    def finish(self):
        self.done = True
        return self
    
    def is_done(self):
        return self.done

    def timer(self):
        self.time +=1
        return self.time
