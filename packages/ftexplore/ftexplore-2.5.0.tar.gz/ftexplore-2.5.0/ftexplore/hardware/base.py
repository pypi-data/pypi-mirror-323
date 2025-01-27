import logging

from .. import module


logger = logging.getLogger(__name__);


class HardwareBase(module.Module):
    '''Abstract base class for hardware'''
    
    inputs = [] # list of current input states
    motor_speeds = [] # list of current motor speeds
    
    def __init__(self):
        '''Instance initialization'''
        self.name = 'hardware'
        self.motor_speeds = [ None ] * 4
        self.inputs = [ None ] * 8
    
    def on_startup(self, metadata):
        '''Tasks to be executed on startup'''
        # Motors
        for i in range(4):
            self.set_motor(i, 0)
        # Inputs
        for i in range(8):
            self.get_input(i)
    
    def on_quit(self, metadata):
        '''Tasks to be executed on shutdown'''
        pass # method is only here so that a consumer exists for this event to avoid a logger warning
        
    def set_motor_hardware(self, num, speed, metadata={}):
        '''Set motor hardware (to be overwritten by child class)'''
        pass
    
    def set_motor(self, num, speed, metadata={}):
        '''Set a motor to the provided speed'''
        if self.motor_speeds[num] != speed:
            self.motor_speeds[num] = speed
            self.set_motor_hardware(num, speed, metadata)
            if metadata is None:
                source_objid = None
            else:
                source_objid = metadata.get('source_objid')
            self.enqueue_event('on_motor_set', metadata={'source_objid_request': source_objid}, num=num, speed=speed)

    def on_motor_set_requested(self, metadata, num, speed):
        '''React on external event to change motor speed'''
        self.set_motor(num, speed, metadata)
        
    def on_alloff_requested(self, metadata):
        '''React on external event to switch-off all motors'''
        for i in range(4):
            self.set_motor(i, 0) # don't propagate metadata here since otherwise "on_motor_set" would not be propagated to source later

    def get_input_hardware(self, num):
        '''Get the state of an input (to be overwritten by child class)'''
        return None

    def get_input(self, num):
        '''Get and propagate current input state'''
        state = self.get_input_hardware(num)
        self.propagate_input_onchange(num, state)

    def on_input_set_hardware(self, num, newvalue, metadata={}):
        '''Method to be called when hardware input state changed'''
        self.propagate_input_onchange(num, newvalue)

    def propagate_input_onchange(self, num, value, metadata={}):
        '''Trigger an event in case the input changed'''
        if self.inputs[num] != value:
            self.inputs[num] = value
            self.enqueue_event('on_input_set', num=num, newvalue=value, metadata={})
