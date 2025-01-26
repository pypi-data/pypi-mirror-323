#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import traceback

from .ftinterface import InterruptRequestedException
from .. import module


logger = logging.getLogger(__name__);


class UserFile(module.Module):
    '''Prepares and controls execution of a Python file provided by the user'''

    _filename = None # the filename of the file with the user code
    _flatvars = False # whether variables can be accessed without prefixing "ft." in user code
    _ft = None # the interface to the devices

    def __init__(self, ft, flatvars=True):
        '''Constructor'''
        self._flatvars = flatvars
        self._ft = ft

    @property
    def filename(self):
        return self._filename
        
    @filename.setter
    def filename(self, value):
        self._filename = value

    def get_bytecode(self):
        '''Accesses the code file and compiles it to bytecode'''
        if not os.access(self._filename, os.R_OK):
            logger.warning('Python file [{name}] does not exist or cannot be read'.format(name=self._filename))
            return None
        try:
            data = open(self._filename, encoding='UTF-8').read()
            data = data.lstrip('\ufeff') # remove BOM
            return compile(data, self._filename, 'exec')
        except Exception as e:
            #logger.exception('Exception when compiling [{name}]: {e}'.format(name=self._filename, e=e))
            text = 'Exception when compiling user code: {e}'.format(e=e)
            logger.info(text)
            trace = traceback.format_exc(limit=0)
            text = '\n' + text + '\n' + trace + '\n'
            self.enqueue_event('on_usercode_output_requested', text=text) # provide information on this exception
            return None

    def run(self):
        '''Run the user code'''
        code = self.get_bytecode()
        if code is None:
            return;
        global ft
        ft = self._ft
        if self._flatvars:
            # Note that properties like "input1" can't be passed out of class instance scope (we would just get the current property value or a property object)
            global analog, input, motor
            analog = ft.analog
            input = ft.input
            motor = ft.motor
            global motor1, motor2, motor3, motor4
            motor1 = ft.motor1
            motor2 = ft.motor2
            motor3 = ft.motor3
            motor4 = ft.motor4
            global output1, output2, output3, output4
            output1 = ft.output1
            output2 = ft.output2
            output3 = ft.output3
            output4 = ft.output4
            global sleep, check_condition, wait_for, write
            sleep = ft.sleep
            check_condition = ft.check_condition
            wait_for = ft.wait_for
            write = ft.write            
        try:
            ft.reset_changes() # start code in clean state
            self.enqueue_event('on_usercode_output_requested', text='*** Execution of user code started ***\n')
            exec(code)
            self.enqueue_event('on_usercode_output_requested', text='\n*** Execution of user code finished ***\n')
        except SystemExit:
            # Ignore exit() call in user code
            logger.debug('User code requested exit')
        except InterruptRequestedException as e:
            logger.debug('User code terminated as requested')
            text = '\n*** ' + str(e) + ' ***\n'
            self.enqueue_event('on_usercode_output_requested', text=text) # provide information on this exception
            self.enqueue_event('on_alloff_requested') # make sure that all motors are stopped in this exception scenario
        except Exception as e:
            # Catch all the exceptions in the user code
            tb = sys.exc_info()[2]
            trace = traceback.format_tb(tb)
            tb = traceback.extract_tb(tb)[-1]
            text = 'Exception in user code [{name}] in line {line} in method "{method}": {e}'.format(name=tb[0], line=tb[1], method=tb[2], e=e)
            logger.info(text)
            text = '\n' + text + '\nTraceback (most recent call last):\n' + ''.join(trace) + '\n'
            self.enqueue_event('on_usercode_output_requested', text=text) # provide information on this exception
            self.enqueue_event('on_alloff_requested') # make sure that all motors are stopped in this exception scenario


if __name__ == '__main__':
    userfile = UserFile(None, False)
    userfile.filename = 'example.py'
    userfile.run()
