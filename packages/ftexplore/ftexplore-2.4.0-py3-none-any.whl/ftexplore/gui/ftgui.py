#! /usr/bin/env python
#  -*- coding: utf-8 -*-

import logging
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox


try:
    # For testing just this file
    import tooltip
    import scrolledtext
    Module = object
except ImportError:
    # Regular operation as module of the application
    from . import tooltip
    from . import scrolledtext
    from ..module import Module


logger = logging.getLogger(__name__);


def init_gui(enqueuing_func=None, scheduling_func=None):
    '''Initialize the GUI objects'''
    root = tk.Tk()
    top = FTGUI_Top(root, enqueuing_func, scheduling_func)
    return root, top

def run_gui(root):
    '''Start and run the GUI event loop'''
    root.focus()
    root.mainloop()


class FTGUI_Top(Module):
    '''Module for the Tk-based main window'''

    _code_filename = '' # name of file with user code
    code_maxlines = 200 # the number of lines to keep in the code text field
    _code_state = 'off' # state of user code execution: off vs. selected vs. running
    motorstickyness = 20 # don't allow very slow motor speeds (0,5,10,...; 0 disables stickyness)

    def __init__(self, top, enqueuing_func = None, scheduling_func=None):
        '''Configure and populate the toplevel window'''
        # Init member variables and properties
        self.name = 'gui'
        self.enqueuing_func = enqueuing_func
        self.scheduling_func = scheduling_func
        # Prepare Tk
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == 'win32':
            self.style.theme_use('winnative')
        self.style.configure('.', background=_bgcolor)
        self.style.configure('.', foreground=_fgcolor)
        self.style.map('.', background=[('selected', _compcolor), ('active', _ana2color)])
        # Window configuration
        self.top = top
        top.geometry('800x540+100+80')
        top.title('FT Explore')
        self.configure_design(top, ['background', 'highlightbackground', 'highlightcolor'])
        top.minsize(692, 250)
        top.maxsize(1920, 1080)
        top.grid_rowconfigure(1, weight=1, minsize=250)
        top.grid_rowconfigure(2, weight=6, minsize=0) # minsize 0 or 80 - depending on whether code frame shall be able to be hidden completely
        for i in range(1, 6):
            top.grid_columnconfigure(i, weight=0, minsize=128)
        top.grid_columnconfigure(6, weight=1, minsize=30)
        # Variables
        self.values_inputs = [ tk.BooleanVar(name='input{0}'.format(i)) for i in range(8) ]
        self.values_motors = [ tk.IntVar(name='motor{0}'.format(i)) for i in range(4) ]
        # Window's controls
        self.FrameMotor = [None]*4
        for i in range(4):
            self.insert_frame_motor(i)
        self.insert_frame_input()
        self.insert_frame_code()
        self.insert_frame_alloff()
        # Common control configuration
        for child in top.winfo_children(): child.grid_configure(padx=3, pady=3)
        # Trace variables
        for i in range(4):
            self.values_motors[i].trace(mode='w', callback=lambda varname, elementname, mode: self.on_motor_set_requested_tk(varname))
        # Trigger scheduled processing
        if self.scheduling_func is not None:
            self.top.after(100, self.on_timer)

    def configure_design(self, ctrl, attrs):
        '''Configure the given control's parameters to values set centrally in this method'''
        if 'activebackground' in attrs:
            ctrl.configure(activebackground='#ececec')
        if 'activeforeground' in attrs:
            ctrl.configure(activeforeground='#000000')
        if 'background' in attrs:
            ctrl.configure(background='#d9d9d9')
        if 'borderwidth' in attrs:
            ctrl.configure(borderwidth='2')
        if 'font' in attrs:
            ctrl.configure(font='TkDefaultFont')
        if 'foreground' in attrs:
            ctrl.configure(foreground='#000000') # black
        if 'disabledforeground' in attrs:
            ctrl.configure(disabledforeground='#a3a3a3')
        if 'highlightbackground' in attrs:
            ctrl.configure(highlightbackground='#d9d9d9')
        if 'highlightcolor' in attrs:
            ctrl.configure(highlightcolor='black')
        if 'insertbackground' in attrs:
            ctrl.configure(insertbackground='black')
        if 'relief' in attrs:
            ctrl.configure(relief='groove')
        if 'selectbackground' in attrs:
            ctrl.configure(selectbackground='#c4c4c4')
        if 'selectforeground' in attrs:
            ctrl.configure(selectforeground='black')
        if 'troughcolor' in attrs:
            ctrl.configure(troughcolor='#d9d9d9')
           
    def insert_frame_motor(self, num):
        '''Insert a Tk frame with motor controls'''
        self.FrameMotor[num] = tk.Frame(self.top)
        self.FrameMotor[num].grid(column=num+1, row=1, sticky='nswe')
        self.configure_design(self.FrameMotor[num], ['background', 'borderwidth', 'highlightbackground', 'highlightcolor', 'relief'])
        self.ScaleSpeed = tk.Scale(self.FrameMotor[num], from_=100.0, to=-100.0)
        self.ScaleSpeed.place(relx=0.08, rely=0.038, relwidth=0.0, relheight=0.777, width=50, bordermode='ignore')
        self.configure_design(self.ScaleSpeed, ['activebackground', 'background', 'foreground', 'highlightbackground', 'highlightcolor', 'troughcolor'])
        self.ScaleSpeed.configure(length='200')
        self.ScaleSpeed.configure(showvalue='0')
        self.ScaleSpeed.configure(resolution='5')
        self.ScaleSpeed.configure(tickinterval='-100.0')
        self.ScaleSpeed.configure(variable=self.values_motors[num])
        self.ButtonForward = tk.Button(self.FrameMotor[num])
        self.ButtonForward.place(relx=0.52, rely=0.057, height=24, width=54)
        self.configure_design(self.ButtonForward, ['activebackground', 'activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.ButtonForward.configure(pady='0')
        self.ButtonForward.configure(text='Forward')
        self.ButtonForward.configure(command=lambda: self.set_motor(num, 100))
        self.ButtonOff = tk.Button(self.FrameMotor[num])
        self.ButtonOff.place(relx=0.52, rely=0.377, height=24, width=28)
        self.configure_design(self.ButtonOff, ['activebackground', 'activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.ButtonOff.configure(pady='0')
        self.ButtonOff.configure(text='Off')
        self.ButtonOff.configure(command=lambda: self.set_motor(num, 0))
        self.ButtonReverse = tk.Button(self.FrameMotor[num])
        self.ButtonReverse.place(relx=0.52, rely=0.698, height=24, width=51)
        self.configure_design(self.ButtonReverse, ['activebackground', 'activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.ButtonReverse.configure(pady='0')
        self.ButtonReverse.configure(text='Reverse')
        self.ButtonReverse.configure(command=lambda: self.set_motor(num, -100))
        self.SpinboxSpeed = tk.Spinbox(self.FrameMotor[num], from_=1.0, to=100.0)
        self.SpinboxSpeed.place(relx=0.08, rely=0.868, relheight=0.064, relwidth=0.36)
        self.configure_design(self.SpinboxSpeed, ['disabledforeground', 'font', 'foreground', 'highlightcolor', 'insertbackground', 'selectbackground', 'selectforeground'])
        self.SpinboxSpeed.configure(activebackground='#f9f9f9')
        self.SpinboxSpeed.configure(background='white')
        self.SpinboxSpeed.configure(buttonbackground='#d9d9d9')
        self.SpinboxSpeed.configure(highlightbackground='black')
        self.SpinboxSpeed.configure(textvariable=self.values_motors[num])
        self.SpinboxSpeed.configure(from_=-100)
        self.SpinboxSpeed.configure(to=100)
        self.SpinboxSpeed.configure(increment=5)
        #self.SpinboxSpeed.bind('<Button-1>', lambda e:ftgui_support.xxx(e))
        self.LabelInfo = tk.Label(self.FrameMotor[num])
        self.LabelInfo.place(relx=0.48, rely=0.849, height=21, width=59)
        self.configure_design(self.LabelInfo, ['activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.LabelInfo.configure(activebackground='#f9f9f9')
        self.LabelInfo.configure(text='Motor M{0}'.format(num+1))

    def insert_frame_input(self):
        '''Inserts a Tk frame with input controls'''

        def set_input(num):
            control = tk.Checkbutton(self.FrameInput)
            self.configure_design(control, ['activebackground', 'activeforeground', 'background', 'foreground', 'highlightbackground', 'highlightcolor'])
            control.configure(disabledforeground='#000000')
            control.configure(state='disabled')
            control.configure(text='Input E{0}'.format(num+1))
            control.configure(variable=self.values_inputs[num])
            return control

        self.FrameInput = tk.Frame(self.top)
        self.FrameInput.grid(column=5, row=1, sticky='nswe')
        self.configure_design(self.FrameInput, ['background', 'borderwidth', 'highlightbackground', 'highlightcolor', 'relief'])
        self.CheckbuttonInput1 = set_input(0)
        self.CheckbuttonInput1.place(relx=0.105, rely=0.038, relheight=0.094, relwidth=0.747)
        self.CheckbuttonInput2 = set_input(1)
        self.CheckbuttonInput2.place(relx=0.105, rely=0.113, relheight=0.094, relwidth=0.747)
        self.CheckbuttonInput3 = set_input(2)
        self.CheckbuttonInput3.place(relx=0.105, rely=0.189, relheight=0.094, relwidth=0.747)
        self.CheckbuttonInput4 = set_input(3)
        self.CheckbuttonInput4.place(relx=0.105, rely=0.264, relheight=0.094, relwidth=0.747)
        self.CheckbuttonInput5 = set_input(4)
        self.CheckbuttonInput5.place(relx=0.105, rely=0.34, relheight=0.094, relwidth=0.747)
        self.CheckbuttonInput6 = set_input(5)
        self.CheckbuttonInput6.place(relx=0.105, rely=0.415, relheight=0.094, relwidth=0.747)
        self.CheckbuttonInput7 = set_input(6)
        self.CheckbuttonInput7.place(relx=0.105, rely=0.491, relheight=0.094, relwidth=0.747)
        self.CheckbuttonInput8 = set_input(7)
        self.CheckbuttonInput8.place(relx=0.105, rely=0.566, relheight=0.094, relwidth=0.747)
        self.EntryAnalog1 = tk.Entry(self.FrameInput)
        self.EntryAnalog1.place(relx=0.158, rely=0.755, height=19, relwidth=0.358)
        self.configure_design(self.EntryAnalog1, ['highlightbackground', 'highlightcolor', 'insertbackground', 'selectbackground', 'selectforeground'])
        self.EntryAnalog1.configure(background='white')
        self.EntryAnalog1.configure(disabledforeground='#a3a3a3')
        self.EntryAnalog1.configure(font='TkFixedFont')
        self.EntryAnalog1.configure(foreground='#000000')
        self.EntryAnalog1.configure(state='disabled')
        tooltip.ToolTip(self.EntryAnalog1, 'TkDefaultFont', 'Value of analog input A1', delay=0.5)
        self.EntryAnalog2 = tk.Entry(self.FrameInput)
        self.EntryAnalog2.place(relx=0.158, rely=0.849, height=19, relwidth=0.358)
        self.configure_design(self.EntryAnalog2, ['highlightbackground', 'highlightcolor', 'insertbackground', 'selectbackground', 'selectforeground'])
        self.EntryAnalog2.configure(background='white')
        self.EntryAnalog2.configure(disabledforeground='#a3a3a3')
        self.EntryAnalog2.configure(font='TkFixedFont')
        self.EntryAnalog2.configure(foreground='#000000')
        self.EntryAnalog2.configure(state='disabled')
        tooltip.ToolTip(self.EntryAnalog2, 'TkDefaultFont', 'Value of analog input A2', delay=0.5)
        self.LabelAnalog1 = tk.Label(self.FrameInput)
        self.LabelAnalog1.place(relx=0.579, rely=0.755, height=19, width=19)
        self.configure_design(self.LabelAnalog1, ['activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.LabelAnalog1.configure(activebackground='#f9f9f9')
        self.LabelAnalog1.configure(text='A1')
        self.LabelAnalog2 = tk.Label(self.FrameInput)
        self.LabelAnalog2.place(relx=0.579, rely=0.849, height=19, width=19)
        self.configure_design(self.LabelAnalog2, ['activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.LabelAnalog2.configure(activebackground='#f9f9f9')
        self.LabelAnalog2.configure(text='A2')

    def insert_frame_alloff(self):
        '''Inserts a Tk frame with an "all off" button'''
        self.FrameAllOff = tk.Frame(self.top)
        #self.FrameAllOff.place(relx=0.706, rely=0.0, relheight=0.491, relwidth=0.294)
        self.FrameAllOff.grid(column=6, row=1, sticky='nswe')
        self.configure_design(self.FrameAllOff, ['background', 'borderwidth', 'highlightbackground', 'highlightcolor', 'relief'])
        self.ButtonAllOff = tk.Button(self.FrameAllOff)
        self.ButtonAllOff.pack(fill='both',expand=1, padx=3, pady=3)
        self.configure_design(self.ButtonAllOff, ['activebackground', 'activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.ButtonAllOff.configure(command=self.on_button_alloff)
        self.ButtonAllOff.configure(pady='0')
        self.ButtonAllOff.configure(text='All Off')

    def insert_frame_code(self):
        '''Inserts a Tk frame for controlling user code'''
        self.FrameCode = tk.Frame(self.top)
        self.FrameCode.grid(column=1, row=2, columnspan=6, sticky='nswe')
        self.configure_design(self.FrameCode, ['background', 'borderwidth', 'highlightbackground', 'highlightcolor', 'relief'])
        self.FrameCode.grid_rowconfigure(1, weight=0, minsize=28)
        self.FrameCode.grid_rowconfigure(2, weight=1, minsize=20)
        self.FrameCode.grid_columnconfigure(1, weight=1)        
        self.ScrolledtextCode = scrolledtext.ScrolledText(self.FrameCode)
        self.ScrolledtextCode.grid(column=1, row=2, sticky='nswe')
        self.configure_design(self.ScrolledtextCode, ['font', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.ScrolledtextCode.configure(background='white')
        self.ScrolledtextCode.configure(insertbackground='black')
        self.ScrolledtextCode.configure(insertborderwidth='3')
        self.ScrolledtextCode.configure(selectbackground='#c4c4c4')
        self.ScrolledtextCode.configure(selectforeground='black')
        self.ScrolledtextCode.configure(state='disabled')
        self.ScrolledtextCode.configure(wrap='char') # char vs word vs none
        self.FrameCodeHeaderrow = tk.Frame(self.FrameCode)
        self.FrameCodeHeaderrow.grid(column=1, row=1, sticky='nswe')
        self.configure_design(self.FrameCodeHeaderrow, ['background', 'highlightbackground', 'highlightcolor'])
        self.FrameCodeHeaderrow.grid_rowconfigure(1, weight=1)
        self.FrameCodeHeaderrow.grid_columnconfigure(1, weight=0, minsize=50)
        self.FrameCodeHeaderrow.grid_columnconfigure(2, weight=0, minsize=50)
        self.FrameCodeHeaderrow.grid_columnconfigure(3, weight=0, minsize=50)
        self.FrameCodeHeaderrow.grid_columnconfigure(4, weight=1)        
        self.ButtonStart = tk.Button(self.FrameCodeHeaderrow)
        self.ButtonStart.grid(column=1, row=1, sticky='nswe')
        self.ButtonStart.grid_configure(padx=3, pady=3)
        self.configure_design(self.ButtonStart, ['activebackground', 'activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.ButtonStart.configure(command=self.on_button_code_start)
        self.ButtonStart.configure(pady='0')
        self.ButtonStart.configure(text='Start')
        self.ButtonStart.configure(state='disabled')
        self.ButtonStop = tk.Button(self.FrameCodeHeaderrow)
        self.ButtonStop.grid(column=2, row=1, sticky='nswe')
        self.ButtonStop.grid_configure(padx=3, pady=3)
        self.configure_design(self.ButtonStop, ['activebackground', 'activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.ButtonStop.configure(command=self.on_button_code_stop)
        self.ButtonStop.configure(pady='0')
        self.ButtonStop.configure(text='Stop')
        self.ButtonStop.configure(state='disabled')
        self.ButtonSelect = tk.Button(self.FrameCodeHeaderrow)
        self.ButtonSelect.grid(column=3, row=1, sticky='nswe')
        self.ButtonSelect.grid_configure(padx=3, pady=3)
        self.configure_design(self.ButtonSelect, ['activebackground', 'activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.ButtonSelect.configure(command=self.on_button_code_select)
        self.ButtonSelect.configure(pady='0')
        self.ButtonSelect.configure(text='Select')
        self.LabelFilename = tk.Label(self.FrameCodeHeaderrow)
        self.LabelFilename.grid(column=4, row=1, sticky='nswe')
        self.LabelFilename.grid_configure(padx=3)
        self.configure_design(self.LabelFilename, ['activeforeground', 'background', 'disabledforeground', 'foreground', 'highlightbackground', 'highlightcolor'])
        self.LabelFilename.configure(activebackground='#f9f9f9')
        self.LabelFilename.configure(anchor='w')
        self.LabelFilename.configure(justify='left')
        self.LabelFilename.configure(text='[no file with user code selected]')
        tooltip.ToolTip(self.LabelFilename, 'TkDefaultFont', 'This is the name of the file containing user code to be executed on demand', delay=0.5)

    @property
    def code_state(self):
        '''Return the current state of user code execution'''
        return self._code_state

    @code_state.setter
    def code_state(self, value):
        '''Manipulate the state of user code execution in a consistent manner'''
        if self._code_state != value:
            if value == 'off':
                self.ButtonSelect.configure(state='normal')
                self.ButtonStop.configure(state='disabled')
                self.ButtonStart.configure(state='disabled')
            elif value == 'selected':
                self.ButtonSelect.configure(state='normal')
                self.ButtonStop.configure(state='disabled')
                self.ButtonStart.configure(state='normal')
            elif value == 'running':
                self.ButtonSelect.configure(state='disabled')
                self.ButtonStop.configure(state='normal')
                self.ButtonStart.configure(state='disabled')
                self.enqueue_event('on_start_code_requested', filename=self._code_filename)
            else:
                logger.error('Tried to set invalid code state [{0}]'.format(value))
            self._code_state = value

    def set_input(self, num, newvalue: bool):
        '''Sets value for an input control'''
        self.values_inputs[num].set(newvalue)

    def set_motor(self, num, newvalue: int):
        '''Sets value for a motor'''
        self.values_motors[num].set(newvalue)

    def write_text(self, text):
        '''Writes text to the output text control'''
        log = self.ScrolledtextCode
        numlines = int(log.index('end - 1 line').split('.')[0])
        log['state'] = 'normal'
        log.insert('end', text)
        if numlines >= self.code_maxlines:
            log.delete('1.0', '{0}.0'.format(numlines-self.code_maxlines+2))
        if log.index('end-1c') != '1.0':
            log.insert('end', '\n')
        log['state'] = 'disabled'
        log.yview_moveto(1) # scroll to the end

    def on_button_alloff(self):
        '''React on pressing "all off" button'''
        logger.debug('Button pressed [AllOff]')
        self.enqueue_event('on_alloff_requested')

    def on_button_code_start(self):
        '''React on pressing "start" button'''
        logger.debug('Button pressed [Start]')
        self.code_state = 'running'
        
    def on_button_code_stop(self):
        '''React on pressing "stop" button'''
        logger.debug('Button pressed [Stop]')
        if self._code_state == 'running': # if the code was running, we need to make sure it's stopped
            self.enqueue_event('on_stop_code_requested')
        self.code_state = 'selected'
        
    def on_button_code_select(self):
        '''React on pressing "select" button'''
        logger.debug('Button pressed [Select]')
        filename = tk.filedialog.askopenfilename()
        if len(filename) > 0:
            self._code_filename = filename
            logger.debug('Filename set to [{0}]'.format(self._code_filename))
            self.LabelFilename.configure(text=self._code_filename)
            self.code_state = 'selected'

    def on_motor_set_requested_tk(self, varname):
        '''Called when the setting for a given motor changes via Tk control'''
        num = int(varname[-1]) # last character of variable name is the motor number 0..3
        newvalue = self.values_motors[num].get()
        if (0 < abs(newvalue) < self.motorstickyness):
            if 0 < newvalue <= 5: # handle spinbox button so that 0 can be left
                self.set_motor(num, self.motorstickyness)
            elif -5 <= newvalue < 0: # handle spinbox button so that 0 can be left
                self.set_motor(num, -self.motorstickyness)
            else:
                self.set_motor(num, 0)
        newvalue = self.values_motors[num].get() # need to get again since we might have changes it above
        self.enqueue_event('on_motor_set_requested', num=num, speed=newvalue)
        logger.debug('Motor M{0} set to [{1}]'.format(num, newvalue))

    def on_show_messagebox_requested(self, message, title=None, type=None):
        '''Shows a message dialog box'''
        if type == 'error':
            if title is None:
                title = 'Error'
            tk.messagebox.showerror(title=title, message=message)
        elif type == 'warning':
            if title is None:
                title = 'Warning'
            tk.messagebox.showwarning(title=title, message=message)
        else:
            if title is None:
                title = 'Information'
            tk.messagebox.showinfo(title=title, message=message)

    def on_timer(self):
        '''Regularly called timer routine'''
        try:
            if self.scheduling_func(): # if something happened...
                self.top.after(25, self.on_timer) # ...check again earier...
            else:
                self.top.after(150, self.on_timer) # ...than otherwise
        except: # even on exception check for future events
            self.top.after(150, self.on_timer)
            raise

    def on_input_set(self, metadata, num, newvalue: bool):
        '''React on change of an input; called from external'''
        self.set_input(num, newvalue)
    
    def on_motor_set(self, metadata, num, speed):
        '''React on change of motor speed; called from external'''
        if self.values_motors[num].get() != speed:
            if speed == None:
                speed = 0
            self.values_motors[num].set(speed)
    
    def on_usercode_output_requested(self, metadata, text):
        '''React on output due to user code; called from external'''
        self.write_text(text)

    def on_usercode_terminated(self, metadata):
        '''Called when the user's code was interrupted; called from external'''
        self.code_state = 'selected'


if __name__ == '__main__':
    root, _ = init_gui()
    run_gui(root)
