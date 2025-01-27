# -*- coding: utf-8 -*-

import logging
import sys
import time

from .. import module_caching


logger = logging.getLogger(__name__);

try:
    import keyboard
except ImportError:
    logger.warning('Python module [keyboard] not installed; checking on keyboad events will not be possible')


class InterruptRequestedException(Exception):
    '''User-defined exception used to interrupt user code'''
    pass


class Motor(object):
    '''Class providing operations for controlling a numbered motor'''

    callback_func = None # callback function for controlling the motor
    num = None # number of this motor

    def __init__(self, num, callback_func):
        '''Constructor to set member variables based on the provided arguments'''
        self.num = num
        self.callback_func = callback_func
    
    def set(self, speed: int):
        '''Set motor to a new speed'''
        if (speed < -100) or (speed > 100):
            raise ValueError('Speed for motor{num} out of allowed range (-100..100)'.format(num=num))
        self.callback_func(self.num, speed)

    def forward(self):
        '''Set motor to full forward speed'''
        self.set(100)

    def reverse(self):
        '''Set motor to full reverse speed'''
        self.set(-100)

    def on(self):
        '''Set motor to full (forward) speed'''
        self.set(100)

    def off(self):
        '''Switch-off motor'''
        self.set(0)

    def stop(self):
        '''Stop motor immediately'''
        self.set(None)


class FTInterface(module_caching.ModuleCaching):
    '''Interface to motors and sensors made available in user code'''

    _interrupt_requested = None # flag indicating whether user code shall be interrupted or not
    motors = None # list of objects representing the motors
    changed = None # dictionary of changed input values
    timestamp = 0 # timestamp in milliseconds since last reset of changes
    check_keys = None # keyboard keys to check for

    def __init__(self, interrupt_requested):
        '''Constructor'''
        super().__init__()
        self.motors = [ Motor(i, self.set_motor) for i in range(4) ]
        self._interrupt_requested = interrupt_requested
        self.reset_changes()

    def on_input_set(self, metadata, num, newvalue):        
        '''React on change of an input; called from external'''
        if self.inputs[num] != newvalue:
            self.changed[f'input{num + 1}'] = newvalue
        super().on_input_set(metadata, num, newvalue)
        
    def get_timestamp_ms(self):
        '''Returns a timestamp in milliseconds'''
        # Python 3.7+ provides time.time_ns(); however, use the less portable old way for backwards compatiblity
        # An alternative would be datetime.now().timestamp() to return seconds (and fractions of them) after 1970-01-01.
        return int(time.time() * 1000)

    def check_for_interruption_request(self):
        '''Stop execution of user code if requested'''
        if self._interrupt_requested.is_set():
            logger.debug('User code execution interrupted')
            raise InterruptRequestedException('Code execution interrupted')

    def set_motor(self, num, speed):
        '''Set speed of specified motor (not to be used by user)'''
        self.enqueue_event('on_motor_set_requested', num=num, speed=speed)
        self.check_for_interruption_request()

    def analog(self, num: int):
        '''Provide current value of a analog input'''
        pass # ***
        self.check_for_interruption_request()

    @property        
    def analog1(self):
        return self.analog(1)
    @property
    def analog2(self):
        return self.analog(2)

    def input(self, num: int):
        '''Provide current value of a digital input'''
        self.check_for_interruption_request()
        return self.inputs[num - 1]
    
    @property
    def input1(self):
        return self.input(1)
    @property        
    def input2(self):
        return self.input(2)
    @property        
    def input3(self):
        return self.input(3)
    @property        
    def input4(self):
        return self.input(4)
    @property        
    def input5(self):
        return self.input(5)
    @property        
    def input6(self):
        return self.input(6)
    @property        
    def input7(self):
        return self.input(7)
    @property        
    def input8(self):
        return self.input(8)

    def motor(self, num: int, speed: int = 9999):
        '''Return a motor object or set the motor's speed (in case a speed is provided)'''
        if (num < 1) or (num > 4):
            raise ValueError('Invalid motor accessed, allowed numbers are 1..4')
        if speed == 9999:
            return self.motors[num - 1]
        else:
            self.motors[num - 1].set(speed)

    @property
    def motor1(self):
        return self.motors[0]
    @property
    def motor2(self):
        return self.motors[1]
    @property
    def motor3(self):
        return self.motors[2]
    @property
    def motor4(self):
        return self.motors[3]

    @property
    def output1(self):
        return self.motors[0]
    @property
    def output2(self):
        return self.motors[1]
    @property
    def output3(self):
        return self.motors[2]
    @property
    def output4(self):
        return self.motors[3]

    def sleep(self, sec):
        '''Wait as long as requested in an interruptible manner'''
        millisec = int(sec * 1000)
        # Multiples of 0.1s
        for i in range(millisec // 100):
            time.sleep(0.1)
            self.check_for_interruption_request()
            self.check_for_keyboard()
        # Remaining time < 0.1s
        time.sleep((millisec % 100) / 1000)

    def reset_changes(self):
        '''Reset the dictionary of changed input values'''
        self.changed = dict()
        self.timestamp = self.get_timestamp_ms()
        self.check_keys = None

    def check_for_keyboard(self):
        '''Check on keyboard event'''
        if self.check_keys is None:
            return
        for key in self.check_keys:
            if keyboard.is_pressed(key):
                keyboard.read_key() # remove key from keyboard buffer
                self.changed['keys'] = key
                break

    def check_condition(self, input1 = None, input2 = None, input3 = None, input4 = None, input5 = None, input6 = None, input7 = None, input8 = None, changed = None, keys = None, timeout = None):
        '''Check (non-blocking) whether one of the given conditions is met'''
        result = False
        if changed == None:
            changed = []
        if keys == None:
            keys = []
        else:
            if 'keyboard' not in sys.modules:
                self.write('You need to install the "keyboard" Python module to react on keyboard events')
            import keyboard  # make available in local scope or force exception
        self.check_keys = keys
        # Check input states
        if input1 is not None:
            if self.input1 == input1:
                result = True
        if input2 is not None:
            if self.input2 == input2:
                result = True
        if input3 is not None:
            if self.input3 == input3:
                result = True
        if input4 is not None:
            if self.input4 == input4:
                result = True
        if input5 is not None:
            if self.input5 == input5:
                result = True
        if input6 is not None:
            if self.input6 == input6:
                result = True
        if input7 is not None:
            if self.input7 == input7:
                result = True
        if input8 is not None:
            if self.input8 == input8:
                result = True
        # Check for changed inputs
        if ('input1' in changed) and ('input1' in self.changed):
            result = True
        if ('input2' in changed) and ('input2' in self.changed):
            result = True
        if ('input3' in changed) and ('input3' in self.changed):
            result = True
        if ('input4' in changed) and ('input4' in self.changed):
            result = True
        if ('input5' in changed) and ('input5' in self.changed):
            result = True
        if ('input6' in changed) and ('input6' in self.changed):
            result = True
        if ('input7' in changed) and ('input7' in self.changed):
            result = True
        if ('input8' in changed) and ('input8' in self.changed):
            result = True
        # Check for keyboard input
        if keys:
            self.check_for_keyboard()
            if any(key for key in keys if key in self.changed.get('keys', [])): # list intersection
                result = True
        # Check whether timeout value is reached
        if timeout:
            if (self.get_timestamp_ms() - self.timestamp) > (timeout * 1000):
                self.changed['timeout'] = (self.get_timestamp_ms() - self.timestamp) / 1000
                result = True
        return result

    def wait_for(self, input1 = None, input2 = None, input3 = None, input4 = None, input5 = None, input6 = None, input7 = None, input8 = None, changed = None, keys = None, timeout = None, time_sleep = 0.02, reset_changes_before = True):
        '''Blocking wait until one of the given conditions is met'''
        if reset_changes_before:
            self.reset_changes()
        while not self.check_condition(input1 = input1, input2 = input2, input3 = input3, input4 = input4, input5 = input5, input6 = input6, input7 = input7, input8 = input8,changed = changed, keys = keys, timeout = timeout):
            self.sleep(time_sleep) # don't to busy waiting to thus not waste CPU cycles

    def write(self, text):
        '''Output text'''
        self.enqueue_event('on_usercode_output_requested', text=text)
        self.check_for_interruption_request()
