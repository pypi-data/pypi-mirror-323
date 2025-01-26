import logging
import threading

from . import ftinterface
from . import userfile
from .. import module_caching


logger = logging.getLogger(__name__)


class UserCode(module_caching.ModuleCaching):
    '''Controlling and executing user code in a separate thread'''
    
    _interrupt_requested = None # flag indicating whether user code shall be interrupted or not

    def __init__(self):
        '''Constructor'''
        super().__init__()
        self.name = 'user'
        self._interrupt_requested = threading.Event()
        self.ft = ftinterface.FTInterface(self._interrupt_requested)
        self.uf = userfile.UserFile(self.ft)
        
    @property
    def enqueue_event_func(self):
        return module_caching.ModuleCaching.enqueue_event_func

    @enqueue_event_func.setter
    def enqueue_event_func(self, value):
        module_caching.ModuleCaching.enqueue_event_func = value
        self.ft.enqueue_event_func = value
        self.uf.enqueue_event_func = value

    def run(self, uf):
        '''Worker thread for user code execution'''
        uf.run()
        self.enqueue_event('on_usercode_terminated')

    def stop_code(self):
        '''Triggers code to stop'''
        self._interrupt_requested.set()

    def on_input_set(self, metadata, num, newvalue):        
        '''React on change of an input; called from external'''
        super().on_input_set(metadata, num, newvalue)
        # Propagate event to our ft instance
        self.ft.on_input_set(metadata, num, newvalue) # *** Test

    def on_start_code_requested(self, metadata, filename):
        '''React on external request to start the user code'''
        self._interrupt_requested.clear()
        self.uf.filename = filename
        t = threading.Thread(target=self.run, args=(self.uf,))
        t.start()

    def on_stop_code_requested(self, metadata):
        '''React on external request to interrupt the user code'''
        self.stop_code()
