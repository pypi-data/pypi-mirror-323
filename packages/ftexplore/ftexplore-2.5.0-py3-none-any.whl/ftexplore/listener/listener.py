import asyncio
import concurrent
import json
import logging
import pynng
import threading

from .. import module_caching


logger = logging.getLogger(__name__);


class Event_ts(asyncio.Event):
    '''Event with additional operations'''
    
    def set_ts(self):
        '''Set event in a threadsafe manner'''
        self._loop.call_soon_threadsafe(self.set)

    def clear_ts(self):
        '''Clear event in a threadsafe manner'''
        self._loop.call_soon_threadsafe(self.clear)


class Listener(module_caching.ModuleCaching):
    '''Listener for incoming connections'''

    num_connected = None # number of connected clients
    evt_stop_requested = None # event indicating that shutdown is requested
    listenerurl = None # protocol, address and port of the listener
    send_queue = None # queue for data to be sent
    send_later = None # list of data to be sent once possible
    
    def __init__(self, listen_address_port):
        '''Constructor to initialize member variables'''        
        super().__init__()
        self.name = 'listener'
        self.num_connected = 0        
        self.listenerurl = 'tcp://' + listen_address_port
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
                    if event == 'get_all_requested':
                        # {'event': 'get_all_requested', 'metadata': {...}}
                        logger.debug('Received event [{event}] from [{src}], metadata [{metadata}'.format(event=event, src=source_addr, metadata=metadata))
                        self.on_get_all_requested(metadata)
                    elif event == 'set_motor_requested':
                        # {'event': 'set_motor_requested', 'num': num, 'speed': speed, 'metadata': {...}}
                        num = int(message.get('num'))
                        speed = int(message.get('speed'))
                        logger.debug('Received event [{event}], num=[{num}], speed=[{speed}], from [{src}], metadata [{metadata}]'.format(event=event, num=num, speed=speed, src=source_addr, metadata=metadata))
                        self.enqueue_event('on_motor_set_requested', num=num, speed=speed, metadata=metadata)
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
                item = json.dumps(item)
                for pipe in sock.pipes:
                    await pipe.asend(item.encode())
        except concurrent.futures._base.CancelledError:
            logger.debug('send loop cancelled')
        except Exception as e:
            logger.critical('Exception occured: [{0}]'.format(e));
            logger.exception('Exception info:'); # just error but prints traceback

    async def run_async(self, listenerurl):
        '''Asynchronously executed code'''
        with pynng.Pair1(polyamorous=True) as sock:
            self.evt_stop_requested = Event_ts()
            self.send_queue = asyncio.Queue()
            
            def post_connect_callback(pipe):
                self.num_connected += 1
                try:
                    addr = str(pipe.remote_address)
                    logger.info('Got connection from {0}'.format(addr))
                except pynng.exceptions.NNGException:
                    pass
                self.put_send_queue() # send any outstanding items

            def post_disconnect_callback(pipe):
                self.num_connected -= 1
                addr = 'unknown'
                try:
                    addr = str(pipe.remote_address)                    
                except pynng.exceptions.NNGException as e:
                    pass
                logger.info('Client [{0}] disconnected'.format(addr))                    
                    
            sock.add_post_pipe_connect_cb(post_connect_callback)
            sock.add_post_pipe_remove_cb(post_disconnect_callback)
            sock.listen(listenerurl)
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
            self.eventloop.run_until_complete(self.run_async(self.listenerurl))
        finally:
            self.eventloop.close()
        #Python 3.7 version:
        #asyncio.run(main())
        logger.debug('Worker thread ended')
    
    def on_startup(self, metadata):
        '''Initialization done on startup'''
        t = threading.Thread(target=self.run, args=('',))
        t.start()
        
    def on_quit(self, metadata):
        '''Clean-up/finishing tasks on quit; called from external'''
        logger.debug('Ending worker thread cleanly')
        if self.evt_stop_requested is not None:
            self.evt_stop_requested.set_ts()

    def on_get_all_requested(self, metadata):
        '''React on request to get complete status; called when event received from client'''
        if metadata is None:
            source_objid = None
        else:
            source_objid = metadata.get('source_objid')    
        for num in range(4):
            self.put_send_queue({'event': 'motor_set', 'num': num, 'speed': self.motor_speeds[num], 'metadata': {'source_objid_request': source_objid}})
        for num in range(8):
            self.put_send_queue({'event': 'input_set', 'num': num, 'newvalue': self.inputs[num], 'metadata': {'source_objid_request': source_objid}})

    def on_input_set(self, metadata, num, newvalue: bool):
        '''React on change of an input; called from external'''
        super().on_input_set(metadata, num, newvalue)
        self.put_send_queue({'event': 'input_set', 'num': num, 'newvalue': newvalue, 'metadata': metadata})

    def on_motor_set(self, metadata, num, speed: bool):
        '''React on speed change of a motor; called from external'''
        super().on_motor_set(metadata, num, speed)
        self.put_send_queue({'event': 'motor_set', 'num': num, 'speed': speed, 'metadata': metadata})
