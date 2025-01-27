import asyncio
import concurrent
import json
import logging
import pynng
import threading

from . import base


logger = logging.getLogger(__name__);


class Event_ts(asyncio.Event):
    '''Event with additional operations'''
    
    def set_ts(self):
        '''Set event in a threadsafe manner'''
        self._loop.call_soon_threadsafe(self.set)

    def clear_ts(self):
        '''Clear event in a threadsafe manner'''
        self._loop.call_soon_threadsafe(self.clear)


class HardwareRemote(base.HardwareBase):
    '''Connect to a remote listener with real hardware'''

    connected = None # indicated whether connection to remote listener is established
    evt_stop_requested = None # event indicating that shutdown is requested
    remoteurl = None # protocol, address and port of the remote listener
    send_queue = None # queue for data to be sent
    send_later = None # list of data to be sent once possible
    
    def __init__(self, remoteaddr, remote_port):
        '''Instance initialization'''        
        base.HardwareBase.__init__(self)
        self.connected = False
        self.name = 'hw_remote'
        self.remoteurl = 'tcp://' + str(remoteaddr) + ':' + str(remote_port)
        self.send_later = []
 
    def message_to_dict(self, message):
        '''Parse received JSON string to Python dictionary'''
        try:
            return json.loads(message)
        except Exception as e:
            logger.debug('Exception parsing JSON message: {0}'.format(str(e)))
            return None

    def put_send_queue(self, item=None):
        '''Puts the provided item into the send queue'''
        if self.send_queue is not None:
            # Send already queued items
            for later_item in self.send_later:
                logger.debug('Queuing remembered item [{0}]'.format(item))
                asyncio.run_coroutine_threadsafe(self.send_queue.put(later_item), self.eventloop)
            self.send_later = []
            # Send new item (if present)
            if item is not None:
                asyncio.run_coroutine_threadsafe(self.send_queue.put(item), self.eventloop)
        else:
            logger.debug('Remembering item [{0}] for later sending once send queue is available'.format(item))
            self.send_later.append(item)

    async def recv_loop(self, sock):
        '''Process incoming events from remote side'''
        try:
            while True:
                msg = await sock.arecv_msg()
                if not msg:
                    return
                source_addr = str(msg.pipe.remote_address)
                message = msg.bytes.decode()
                logger.debug('Received message {message} from [{src}]'.format(message=message, src=source_addr))
                message = self.message_to_dict(message)
                if message is None:
                    logger.error('Message [{message}] from [{src}] does not contain valid JSON. Ignored'.format(message=message, src=source_addr))
                else:
                    event = message.get('event', '')
                    metadata = message.get('metadata', {})
                    if event == 'input_set':
                        # {"event": "input_set", "num": 1, "newvalue": 1}
                        num = int(message.get('num'))
                        newvalue = int(message.get('newvalue'))
                        logger.debug('Received event [{event}], num=[{num}], newvalue=[{newvalue}], from [{src}], metadata [{metadata}]'.format(event=event, num=num, newvalue=newvalue, src=source_addr, metadata=metadata))
                        self.on_input_set_hardware(num, newvalue, metadata)
                    elif event == 'motor_set':
                        # {"event": "motor_set", "num": 1, "speed": 100, "metadata": {...}}
                        num = int(message.get('num'))
                        speed = int(message.get('speed'))
                        logger.debug('Received event [{event}], num=[{num}], speed=[{speed}], from [{src}], metadata [{metadata}]'.format(event=event, num=num, speed=speed, src=source_addr, metadata=metadata))
                        self.enqueue_event('on_motor_set', num=num, speed=speed, metadata=metadata)
                    else:
                        logger.error('Message [{message}] from [{src}] does not contain a recognized event. Ignored'.format(message=message, src=source_addr))
        except concurrent.futures._base.CancelledError:
            logger.debug('receive loop cancelled')
        except Exception as e:
            logger.critical('Exception occured: [{0}]'.format(e));
            logger.exception('Exception info:'); # just error but prints traceback

    async def send_loop(self, sock, send_queue):
        '''Send events to remote side once put into the send queue'''
        try:
            while True:
                item = await send_queue.get()
                logger.debug('Sending item {0} to listener'.format(item))
                item = json.dumps(item)
                for pipe in sock.pipes:
                    await pipe.asend(item.encode())
        except concurrent.futures._base.CancelledError:
            logger.debug('send loop cancelled')
        except Exception as e:
            logger.critical('Exception occured: [{0}]'.format(e));
            logger.exception('Exception info:'); # just error but prints traceback

    async def run_async(self, remoteurl):
        '''Asynchronously executed code'''
        with pynng.Pair1(polyamorous=True) as sock:
            self.evt_stop_requested = Event_ts()
            self.send_queue = asyncio.Queue()
            
            def post_connect_callback(pipe):
                self.connected = True
                try:
                    addr = str(pipe.remote_address)
                    logger.info('Established connection to {0}'.format(addr))
                except pynng.exceptions.NNGException:
                    pass
                #self.put_send_queue() # send any outstanding items
                self.put_send_queue({'event': 'get_all_requested'}) # send any outstanding items and get complete status            

            def post_disconnect_callback(pipe):
                self.connected = False
                addr = 'unknown'
                try:
                    addr = str(pipe.remote_address)                    
                except pynng.exceptions.NNGException as e:
                    pass
                logger.info('Disconnected from {0}'.format(addr))
                    
            sock.add_post_pipe_connect_cb(post_connect_callback)
            sock.add_post_pipe_remove_cb(post_disconnect_callback)
            sock.dial(remoteurl)
            task1 = asyncio.ensure_future(self.recv_loop(sock))
            task2 = asyncio.ensure_future(self.send_loop(sock, self.send_queue))
            await self.evt_stop_requested.wait()
            logger.debug('Cleaning up worker thread')
            task1.cancel()
            task2.cancel()

    def run(self, _):
        '''Worker thread for handling the connection'''
        logger.debug('Worker thread started')
        asyncio.set_event_loop(asyncio.new_event_loop()) # needed since we're not working in the main thread
        self.eventloop = asyncio.get_event_loop()
        self.eventloop.set_debug(logger.getEffectiveLevel() <= logging.DEBUG) # in case of INFO, WARN, ERROR,... do not go into debug mode
        try:
            self.eventloop.run_until_complete(self.run_async(self.remoteurl))
        finally:
            self.eventloop.close()
        #Python 3.7 version:
        #asyncio.run(main())
        logger.debug('Worker thread ended')
    
    def on_startup(self, metadata):
        '''Initialization done on startup'''
        base.HardwareBase.on_startup(self, metadata)
        t = threading.Thread(target=self.run, args=('',))
        t.start()
        
    def on_quit(self, metadata):
        '''Clean-up/finishing tasks on quit'''
        base.HardwareBase.on_quit(self, metadata)
        logger.debug('Ending worker thread cleanly')
        if self.evt_stop_requested is not None:
            self.evt_stop_requested.set_ts()
        
    def set_motor_hardware(self, num, speed, metadata={}):
        '''Set motor hardware (num=0..3, speed=-100..100|None)'''
        self.put_send_queue({'event': 'set_motor_requested', 'num': num, 'speed': speed, 'metadata': metadata})
