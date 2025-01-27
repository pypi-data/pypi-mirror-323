# -*- coding: utf-8 -*-

import asyncio
import concurrent
import logging
import queue
import pprint

from .base import EventProcessorBase


logger = logging.getLogger(__name__);


class EventProcessorStandalone(EventProcessorBase):
    '''Class for providing event processing for the application (uses an internal asyncio event loop)'''

    def __init__(self):
        '''Constructor'''
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()

    def handle_exception(self, loop, context):
        '''Handler for exceptions in coroutines'''
        if isinstance(context['exception'], asyncio.CancelledError):
            logger.debug('Async event loop cancelled')
        else:
            logging.error('Caught exception: [{e}] [{m}] [{f}]'.format(e=context.get('exception', ''), m=context.get('message'), f=context.get('future')))

    def eventloop(self):
        '''Run the event processing loop (to be overwritten by child class)'''
        self.loop.set_debug(logger.getEffectiveLevel() <= logging.DEBUG) # in case of INFO, WARN, ERROR,... do not go into debug mode
        try:        
            self.loop.set_exception_handler(self.handle_exception)
            self.loop.run_until_complete(self.run_async())            
        finally:
            for task in asyncio.all_tasks(self.loop):
                task.cancel()
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def enqueue_event(self, event, threadsafe=True, **kwargs):
        '''Put provided event with the provided parameters into the event queue (thread-safe)'''
        item = kwargs
        item['event'] = event
        if threadsafe:
            self.loop.call_soon_threadsafe(self.queue.put_nowait, item)
        else: # this needs to be used in case the eventloop is no longer running to avoid blocking
            self.queue.put_nowait(item)

    async def waitloop(self):
        '''Due to limitations in Windows we need to awake regularly to detect keyboard interrupts'''
        while True:
            await asyncio.sleep(1)

    async def serve_queue(self):
        '''Serve the event queue asynchronously'''
        while True:
            item = await self.queue.get()
            self.process_queue(item)

    async def run_async(self):
        '''Asynchronously executed code'''        
        task1 = asyncio.ensure_future(self.waitloop())
        task2 = asyncio.ensure_future(self.serve_queue())            
        await asyncio.gather(task1, task2)
