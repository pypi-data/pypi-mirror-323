import logging

from . import module


logger = logging.getLogger(__name__);


class ModuleCaching(module.Module):
    '''Extended module that is caching the current hardware state locally'''
    
    inputs = None # list of current input states
    motor_speeds = None # list of current motor speeds
    
    def __init__(self):
        '''Constructor to initialize member variables'''
        super().__init__()
        self.motor_speeds = [ None ] * 4
        self.inputs = [ None ] * 8
    
    def on_input_set(self, metadata, num, newvalue):        
        '''React on change of an input; called from external'''
        self.inputs[num] = newvalue

    def on_motor_set(self, metadata, num, speed):
        '''React on speed change of a motor; called from external'''
        self.motor_speeds[num] = speed
