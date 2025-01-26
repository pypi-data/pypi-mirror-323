import logging

from . import base

logger = logging.getLogger(__name__);


class HardwareBuiltinGPIO(base.HardwareBase):
    '''RaspberryPi GPIOs (using eight inputs)'''

    gpio = None # the GPIO interface for accessing the hardware
    RPi = None # reference to the RPi module
    #gpio_pins = [5, 6, 13, 19, 26, 16, 20, 21] # the pin numbers of the GPIO pins for inputs 0..7 (shown as 1-8)
    gpio_pins = [26, 19, 13, 6, 5, 16, 20, 21] # the pin numbers of the GPIO pins for inputs 0..7 (shown as 1-8)

    def __init__(self):
        '''Instance initialization'''
        base.HardwareBase.__init__(self)
        self.name = 'hw_builtin-gpio'

    def on_startup(self, metadata):
        '''Initialization done on startup'''
        try:
            import RPi.GPIO # import late so that this is only imported if the module is needed
            self.gpio = RPi.GPIO
            self.RPi = RPi
        except ImportError:
            logger.error('Python library "RPi.GPIO" not found, built-in GPIOs cannot be used')
            self.enqueue_event('on_show_messagebox_requested', type='error', title='Library missing', message='Please install Python library "RPi.GPIO" to use this hardware.')
        else:
            # Use Broadcom GPIO numbering
            self.gpio.setmode(self.gpio.BCM);
            # Set-up needed GPIO PINs
            for channel in self.gpio_pins:
                self.gpio.setup(channel, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP);
        finally:
            # Do this late so that hardware is queried only after having been set up
            base.HardwareBase.on_startup(self, metadata)
        # Start listening for input changes
        if self.gpio is not None:
            for channel in self.gpio_pins:
                self.gpio.add_event_detect(channel, RPi.GPIO.BOTH, callback=self.on_gpio_changed);
                logger.debug('Listening on GPIO {0}'.format(channel));

    def on_quit(self, metadata):
        '''Clean-up/finishing tasks on quit'''
        base.HardwareBase.on_quit(self, metadata)
        if self.gpio is not None:
            self.gpio.cleanup()

    def get_input_bychannel(self, channel):
        '''Get state of the given input pin'''
        # Determine the input value (inverse logic due to internal pull-up resistor and switching against ground)
        return (self.gpio.input(channel) != self.RPi.GPIO.HIGH) # HIGH->False, LOW->True
        
    def get_input_hardware(self, num):
        '''Get the state of an input'''
        channel = self.gpio_pins[num]
        return self.get_input_bychannel(channel)

    def on_gpio_changed(self, channel):
        '''Callback routine for GPIO change'''
        value = self.get_input_bychannel(channel)
        self.on_input_set_hardware(self.gpio_pins.index(channel), value)
