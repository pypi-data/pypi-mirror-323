# -*- coding: utf-8 -*-

import logging
import string
import uuid


logger = logging.getLogger(__name__);


class Module(object):
    '''Application module (abstract class)'''

    _enqueue_event_func = None # method for enqueuing events into the event loop
    _name = '' # the name of the module
    _objid = None # unique random identifier of this object


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def objid(self):
        if self._objid is None:
            self._objid = str(uuid.uuid4())[-12:]
        return self._objid

    @property
    def enqueue_event_func(self):
        return self._enqueue_event_func
        
    @enqueue_event_func.setter
    def enqueue_event_func(self, value):
        self._enqueue_event_func = value

    def enqueue_event(self, event, **kwargs):
        '''Put the event with the provided parameters into the event queue'''
        if self.enqueue_event_func is not None:
            kwargs['metadata'] = kwargs.get('metadata', dict()) # make sure metadata dictionary is present
            kwargs['metadata']['source'] = kwargs['metadata'].get('source', self.name)
            kwargs['metadata']['source_objid'] = kwargs['metadata'].get('source_objid', self.objid)
            kwargs['metadata']['source_objid_request'] = kwargs['metadata'].get('source_objid_request', self.objid)
            self.enqueue_event_func(event, **kwargs)
        else:
            logger.error('enqueue_event_func not set')
