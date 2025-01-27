import logging
from . import base

logger = logging.getLogger(__name__);


class HardwareMotorHat(base.HardwareBase):
    '''Adafruit MotorHat/MotorKit hardware (controls four motors)'''

    kit = None # the controller object for the hardware

    def __init__(self):
        '''Instance initialization'''
        base.HardwareBase.__init__(self)
        self.name = 'hw_motorhat'

    def on_startup(self, metadata):
        '''Initialization done on startup'''
        base.HardwareBase.on_startup(self, metadata)
        try:
            from adafruit_motorkit import MotorKit # import late so that this is only imported if the module is needed
            self.kit = MotorKit()
        except ImportError:
            logger.error('Python library "adafruit_motorkit" not found, hardware cannot be used')
            self.enqueue_event('on_show_messagebox_requested', type='error', title='Library missing', message='Please install Python library "adafruit_motorkit" to use this hardware.')
        
    def set_motor_hardware(self, num, speed, metadata={}):
        '''Set motor hardware (num=0..3, speed=-100..100|None)'''
        if self.kit is None:
            return
        if num == 0:
            motor = self.kit.motor1
        elif num == 1:
            motor = self.kit.motor2
        elif num == 2:
            motor = self.kit.motor3
        elif num == 3:
            motor = self.kit.motor4
        if speed is None:
            motor.throttle = None # hard stop
        else:
            motor.throttle = speed / 100
