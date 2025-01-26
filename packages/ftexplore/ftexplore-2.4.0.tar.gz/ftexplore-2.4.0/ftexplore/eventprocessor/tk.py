# -*- coding: utf-8 -*-

import logging
import queue

from .base import EventProcessorBase
from ..gui import ftgui


logger = logging.getLogger(__name__);


class EventProcessorTk(EventProcessorBase):
    '''Class for providing event processing for the application (uses the Tk GUI event loop)'''

    def __init__(self):
        '''Constructor'''
        self.queue = queue.Queue()
        self.gui_root, self.gui_top = ftgui.init_gui(self.enqueue_event, self.process_queue)
    
    def prerun(self):
        '''Prepare running the event processing loop'''
        self.register_module(self.gui_top)

    def postrun(self):
        '''Additional tasks after running the event processing loop'''
        self.deregister_module(self.gui_top.name)

    def eventloop(self):
        '''Run the event processing loop (to be overwritten by child class)'''
        ftgui.run_gui(self.gui_root)
