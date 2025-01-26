# -*- coding: utf-8 -*-

import asyncio
import logging
import queue


logger = logging.getLogger(__name__);


class EventProcessorBase(object):
    '''Class for providing event processing for the application (uses Tk GUI as event loop)'''

    modules = dict() # application module objects that shall receive events
    queue = None # event queue

    def __init__(self):
        '''Constructor'''
        self.queue = queue.Queue()
        self.gui_root, self.gui_top = ftgui.init_gui(self.enqueue_event, self.process_queue)

    def register_module(self, module):
        '''Register new application module object for event triggering and reception'''
        if module is None:
            return
        module.enqueue_event_func = self.enqueue_event
        self.modules[module.name] = module
        
    def deregister_module(self, modulename):
        '''Deregister module object from event reception'''
        del(self.modules[modulename])
    
    def prerun(self):
        '''Prepare running the event processing loop (to be overwritten by child class)'''
        pass

    def postrun(self):
        '''Additional tasks after running the event processing loop (to be overwritten by child class)'''
        pass
        
    def eventloop(self):
        '''Run the event processing loop (to be overwritten by child class)'''
        pass

    def run(self):
        '''Run the event processing loop'''
        # Prepare event loop
        self.prerun()
        self.enqueue_event('on_startup', metadata={'source': 'eventprocessor'})
        try:
            # Run the event loop
            self.eventloop()
        finally: # always clean-up, e.g. on keyboard interrupt
            # Tasks to be executed once event loop has ended
            self.postrun()
            self.enqueue_event('on_quit', metadata={'source': 'eventprocessor'}, threadsafe=False)
            self.process_queue()

    def enqueue_event(self, event, threadsafe=None, **kwargs):
        '''Put provided event with the provided parameters into the event queue (thread-safe)'''
        item = kwargs
        item['event'] = event
        kwargs['metadata'] = kwargs.get('metadata', dict()) # make sure metadata dictionary is present
        self.queue.put(item)
        
    def process_item(self, item):
        '''Process the given queue item (containing event): distribute to consumers (i.e. the modules)'''
        event = item.get('event')
        del(item['event'])
        source = item['metadata'].get('source', None)
        if source is None:
            logger.warning('Event [{0}] does not have an event source specified'.format(event))
        methods = dict()
        for modulename, module in self.modules.items():
            if modulename != source: # split horizon (don't send event back to source)
                module_objid = module.objid
                if (item['metadata'].get('source_objid_request') != module.objid) or (modulename in ['hw_remote', 'listener']): # split horizon (don't send event response back to source of request unless interconnection pipe)
                    try:
                        method = getattr(module, event);
                    except AttributeError:
                        method = None
                    if method is not None:
                        methods[module.name] = method
        if len(methods) == 0:
            logging.warning('No consumer present for event [{0}] in modules {1} (note: not sending back to source)'.format(event, list(self.modules.keys())))
        else:
            logger.debug('Sending event [{0}] with data {1} to consumers {2}'.format(event, item, list(methods.keys())))
        for modulename, method in methods.items():
            method(**item)

    def process_queue(self, item=None):
        '''Process the event queue until it is empty (the first item to be processed can be provided)'''
        count = 0
        try:
            while 1:
                if item is None:
                    item = self.queue.get_nowait()
                count += 1
                self.process_item(item)
                item = None
        except queue.Empty:
            pass
        except asyncio.queues.QueueEmpty:
            pass
        return count # return the number of processed events
