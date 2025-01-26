# Module for ftDuino hardware using the WebUSB IOServer sketch.
#
# Unfortunaletly, inputs need to be polled over the USB interface. Thus, short input value changes cannot be observed and changes are observed with delay.
# The red LED on the hardware is used to indicate that ftExplore is running and connected.
# The ftDuino hardware is capable to control four motors [based on eight analog outputs] and provides eight analog inputs and four counters).

import logging
import queue
import threading

try:
    import usb.core
    import usb.util
    import usb.backend.libusb1
except ModuleNotFoundError:
    print('Could not import required modules!')
    print('Install:')
    print('  python -m pip install libusb')
    print('  python -m pip install pyusb')
    raise  # reraise exception

from . import base


logger = logging.getLogger(__name__)

POLLING_TIME = 100  # poll inputs every 100ms; this is a tradeoff (can be decreased to e.g. 10 while causing higher CPU load)


class WebUSB():
    def __init__(self, vendor_id, product_id, on_data_callback=None, idle_data=None):
        '''Instance initialization'''
        # Initialize instance attributes
        self.thread_receiving = None
        self.thread_sending = None
        self.queue_sending = queue.Queue()
        self.end_event = threading.Event()
        self.on_data_callback = on_data_callback
        self.idle_data = idle_data
        self.polling_time = POLLING_TIME / 1000
        # Find USB device
        self.dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if self.dev is None:
            raise ValueError('Hardware device not found')
        self.cfg = self.dev.get_active_configuration()
        self.intf = usb.util.find_descriptor(self.cfg, bInterfaceNumber=2)

    def connect(self):
        '''Connect to USB device'''
        # Claim the interface
        usb.util.claim_interface(self.dev, self.intf.bInterfaceNumber)
        # Set alternate setting to default (could be omitted)
        self.dev.set_interface_altsetting(interface=2, alternate_setting=0)
        # Perform control transfer (without it, no data is received from ftDuino)
        bmRequestType = usb.util.build_request_type(
            usb.util.CTRL_OUT,                 # transfer direction (OUT) from host to device
            usb.util.CTRL_TYPE_CLASS,          # type (CLASS) indicating request is defined by a USB class
            usb.util.CTRL_RECIPIENT_INTERFACE  # recipient (INTERFACE) indicating the request is for an interface
        )
        bRequest = 0x22         # specific request code (vendor-specific operation)
        wValue = 0x01           # value parameter (activation code/setting for the request)
        wIndex = 0x02           # index parameter (often interface number the request is directed to)
        data_or_wLength = None  # data payload for OUT transfer (None for no additional data)
        self.dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength)
        # Get endpoint references
        for ep in self.intf:
            if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                self.read_in_endpoint = ep
            else:
                self.write_out_endpoint = ep
        if not self.read_in_endpoint or not self.write_out_endpoint:
            raise IOError('Cannot find IN endpoint or OUT endpoint')
        # Reset parser
        self.send(chr(27))  # null byte or ESC resets the parser

    def disconnect(self):
        '''Disconnect the device'''
        # Release the interface
        usb.util.release_interface(self.dev, self.intf.bInterfaceNumber)
        usb.util.dispose_resources(self.dev)
        self.dev = None

    def send(self, data, timeout=1000):
        '''Send data to the device'''
        #logger.debug(f'Writing data [{data}] to device')
        # Write data to the out-endpoint        
        self.write_out_endpoint.write(data, timeout=timeout)

    def thread_send_continuously(self):
        '''Continuously attempt to send data (incl. polling outputs) until notified to stop'''
        while not self.end_event.is_set():
            try:
                data = self.queue_sending.get(timeout=self.polling_time)
                self.send(data)
                self.queue_sending.task_done()
            except queue.Empty:
                if self.idle_data is not None:
                    #logger.debug(f'Send queue is empty, polling outputs')                                    
                    self.send(self.idle_data)

    def receive(self, timeout=1000):
        '''Receive data from the device'''
        try:
            # Read data from the in-endpoint
            data = self.read_in_endpoint.read(64, timeout=timeout)  # assuming 64 is the proper buffer size for your device
            return ''.join(chr(item) for item in data)
        except usb.core.USBError as e:
            if e.backend_error_code == -7:  # LIBUSB_ERROR_TIMEOUT
                #logger.debug('No data received (LIBUSB_ERROR_TIMEOUT)')
                pass
            else:
                logger.error(f'USB error {e.backend_error_code}: {e}')
            return None

    def thread_receive_continuously(self):
        '''Continuously attempt to receive data until notified to stop'''
        while not self.end_event.is_set():
            data = self.receive()
            #logger.debug(f'Read data [{data}] from device')            
            if data:
                self.on_data_callback(data)

    def start_receiving(self):
        '''Start the receiving thread'''
        assert self.thread_receiving == None
        self.thread_receiving = threading.Thread(target=self.thread_receive_continuously)
        self.thread_receiving.start()

    def start_sending(self):
        '''Start the sending thread'''
        assert self.thread_sending == None
        self.thread_sending = threading.Thread(target=self.thread_send_continuously)
        self.thread_sending.start()

    def stop_threads(self):
        '''Stop the receiving thread and the sending thread'''
        assert self.thread_receiving != None
        assert self.thread_sending != None
        self.end_event.set()  # notify thread to stop
        self.thread_sending.join()  # wait for thread to have stopped
        self.thread_receiving.join()  # wait for thread to have stopped

    def schedule_send(self, data):
        '''Schedule sending of data to the device'''
        logger.debug(f'Enqueuing data [{data}] for sending it to device')
        self.queue_sending.put(data)


class HardwareFtDuino(base.HardwareBase):
    '''ftDuino hardware (controls four motors [based on eight analog outputs] and provides eight analog inputs and four counters)'''

    def __init__(self):
        '''Instance initialization'''
        base.HardwareBase.__init__(self)
        self.name = 'hw_ftduino'
        self.ftduino = None
        self.input = 8 * [ None ]

    def on_startup(self, metadata):
        '''Initialization done on startup'''
        # Commands to query all inputs
        items = [ '{"get":{"port":"i' + str(i) + '"}}' for i in range(1, 9) ]
        idle_data = ''.join(items)
        # Look for a specific USB device
        self.ftduino = WebUSB(0x1c40, 0x0538, self.on_data_received, idle_data)
        # Connect to the device
        self.ftduino.connect()
        # Request version info
        self.ftduino.send(b'{"get":"version"}')
        self.set_led(True)
        # Call parent
        base.HardwareBase.on_startup(self, metadata)
        # Start receiving and sending data in a separate thread each
        self.ftduino.start_receiving()
        self.ftduino.start_sending()

    def on_quit(self, metadata):
        '''Clean-up/finishing tasks on quit'''
        assert self.ftduino is not None
        self.set_led(False)
        base.HardwareBase.on_quit(self, metadata)
        # Stop receiving data
        self.ftduino.stop_threads()
        # Disconnect the device
        self.ftduino.disconnect()

    def set_led(self, value):
        '''Switches the red ftDuino LED on or off'''
        data = 'true' if value else 'false'
        data = '{"set":{"port":"led","value":' + data + '}}'
        self.ftduino.schedule_send(data.encode())

    def set_motor_hardware(self, num, speed, metadata={}):
        '''Set motor hardware (num=0..3, speed=-100..100|None)'''
        assert self.ftduino is not None
        assert num >= 0
        assert num <= 3
        motor = str(num + 1)
        if speed < 0:
            mode = 'left'
        elif speed > 0:
            mode = 'right'
        else:
            mode = 'off'
        value = '0' if (speed is None) else str(abs(speed))
        data = '{"set":{"port":"m' + motor + '","mode":"' + mode + '","value":' + value + '}}'
        self.ftduino.schedule_send(data.encode())

    def get_input_hardware(self, num):
        '''Get the state of an input'''
        return self.input[num]

    def on_data_received(self, data):
        '''Process received data'''
        if data.startswith('{ "port": "I'):
            # Evaluate input data
            num = int(data[12]) - 1
            value = (data[26] == "1")
            if self.input[num] != value:
                self.on_input_set_hardware(num, value)
                self.input[num] = value
        elif data.startswith('{ "version": "'):
            # Evaluate version info
            value = data[14:]  # beginning after quotation mark of version string
            value = value.partition('"')[0]  # part before quotation mark after version string
            logger.info(f'Connected to ftDuino with software version {value}')
        else:
            logger.warning(f'Data received (ignored): {data}')
