from . import base


class HardwareDemo(base.HardwareBase):
    '''Demo hardware (i.e. no real hardware)'''
    
    def __init__(self):
        '''Instance initialization'''
        base.HardwareBase.__init__(self)
        self.name = 'hw_demo'

    def set_motor_hardware(self, num, speed, metadata={}):
        '''Set motor hardware'''
        # For each motor to inputs are set to indicate forward vs. reverse moving direction
        self.on_input_set_hardware(num*2, speed>0)
        self.on_input_set_hardware(num*2+1, speed<0)
    
    def get_input_hardware(self, num, metadata={}):
        '''Get the state of an input'''
        return False
