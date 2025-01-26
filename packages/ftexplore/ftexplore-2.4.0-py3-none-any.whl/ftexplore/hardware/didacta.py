import logging
from . import builtingpio

logger = logging.getLogger(__name__);


class HardwareDidacta(builtingpio.HardwareBuiltinGPIO):
    '''Didacta Advanced hardware (controls four motors, eight digital inputs, three analog inputs)'''

    gpio_pins = [5, 6, 16, 17, 18, 19, 26, 27] # the pin numbers of the GPIO pins for inputs 0..7 (shown as 1-8)
    motor_pins_a = [23, 25, 13, 21] # the pin numbers of the GPIO pins for motors 0..3 (shown as 1-4), first output
    motor_pins_b = [22, 24, 12, 20] # the pin numbers of the GPIO pins for motors 0..3 (shown as 1-4), second output
    pwm_a = [None, None, None, None]
    pwm_b = [None, None, None, None]
    startup_done = False

    def __init__(self):
        '''Instance initialization'''
        builtingpio.HardwareBuiltinGPIO.__init__(self)
        self.name = 'hw_didacta'

    def on_startup(self, metadata):
        '''Initialization done on startup'''
        builtingpio.HardwareBuiltinGPIO.on_startup(self, metadata)
        # Setup four motor outputs
        for channel in self.motor_pins_a:
            self.gpio.setup(channel, self.gpio.OUT)
            self.gpio.output(channel, self.gpio.LOW)
        for channel in self.motor_pins_b:
            self.gpio.setup(channel, self.gpio.OUT)
            self.gpio.output(channel, self.gpio.LOW)
        self.startup_done = True

    def ensure_stop_pwm(self, pwm, num):
        '''Make sure that there is no running PWM on the given motor output'''
        if pwm[num] is not None:
            pwm[num].stop()
            pwm[num] = None

    def ensure_stop_pwm_a(self, num):
        '''Make sure that there is no running PWM on the given motor output'''
        self.ensure_stop_pwm(self.pwm_a, num)

    def ensure_stop_pwm_b(self, num):
        '''Make sure that there is no running PWM on the given motor output'''
        self.ensure_stop_pwm(self.pwm_b, num)
 
    def set_pwm(self, pwm, num, output, duty_cycle):
        '''Initialized and/or sets PWM on the given output'''
        if pwm[num] is None:
            pwm[num] = self.gpio.PWM(output, 100)
            pwm[num].start(duty_cycle)
        else:
            pwm[num].ChangeDutyCycle(duty_cycle)

    def set_pwm_a(self, num, speed):
        '''Initialized and/or sets PWM on the given motor'''
        self.set_pwm(self.pwm_a, num, self.motor_pins_a[num], speed)

    def set_pwm_b(self, num, speed):
        '''Initialized and/or sets PWM on the given motor'''
        self.set_pwm(self.pwm_b, num, self.motor_pins_b[num], speed)

    def set_motor_hardware(self, num, speed, metadata={}):
        '''Set motor hardware (num=0..3, speed=-100..100|None)'''
        if not self.startup_done: # no need to stop motors on startup here since this is already done in on_startup
            return
        pin_a = self.motor_pins_a[num]
        pin_b = self.motor_pins_b[num]
        if speed == 0:
            self.ensure_stop_pwm_a(num)
            self.ensure_stop_pwm_b(num)
            self.gpio.output(pin_a, self.gpio.LOW)
            self.gpio.output(pin_b, self.gpio.LOW)
        elif speed == 100:
            self.set_pwm_a(num, speed)
            # self.ensure_stop_pwm_a(num)  motor gets switched off if this is uncommented            
            self.ensure_stop_pwm_b(num)
            self.gpio.output(pin_a, self.gpio.HIGH)
            self.gpio.output(pin_b, self.gpio.LOW)
        elif speed == -100:
            self.ensure_stop_pwm_a(num)
            self.set_pwm_b(num, -speed)
            # self.ensure_stop_pwm_b(num)  motor gets switched off if this is uncommented            
            self.gpio.output(pin_a, self.gpio.LOW)
            self.gpio.output(pin_b, self.gpio.HIGH)
        else:
            if speed > 0:
                self.ensure_stop_pwm_b(num)
                self.set_pwm_a(num, speed)
                self.gpio.output(pin_b, self.gpio.LOW)                                
            else:
                self.ensure_stop_pwm_a(num)
                self.set_pwm_b(num, -speed)
                self.gpio.output(pin_a, self.gpio.LOW)                
