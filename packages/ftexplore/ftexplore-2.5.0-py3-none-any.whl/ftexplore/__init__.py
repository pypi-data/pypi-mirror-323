#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""ft-Explore allows to control motors and to check inputs by GUI and user-provided Python code"""

__author__ = "Dirk Henrici"
__license__ = "GPL3"
__email__ = "ftexplore@henrici.name"


import getopt
import logging
import sys
from ipaddress import ip_address
from urllib.parse import urlparse


def usage():
    '''Show information on command line arguments'''
    print('Usage: %s [-?|--help] [--loglevel debug|info|error] [-g|--gui no|auto|yes] [-h|--hardware <hardware>] [-l|--listen [<address>:]<port>]' % sys.argv[0])
    print('ft-Explore allows to control motors and to check inputs by GUI and user-provided Python code')
    print()
    print('  -?, --help                        show program usage')
    print('  --loglevel debug|info|error       set the level of debug information')
    print('                                    default: info')
    print('  -g, --gui no|auto|yes             whether the GUI shall be shown or not')
    print('                                    default: auto')
    print('  -h, --hardware <hardware>         type of locally available hardware or address of remote hardware')
    print('                                    default: demo')
    print('  -l, --listen [<address>:]<port>   interface address and port to listen for clients')
    print('                                    default: do not listen')
    print()
    print('Examples: Show GUI and use no real hardware for demo purposes (this is the default)')
    print('            %s --loglevel info --hardware demo' % sys.argv[0])
    print('          Show GUI and use the locally available default hardware')
    print('            %s --loglevel debug --hardware default' % sys.argv[0])
    print('          Distributed operation with local GUI and remote hardware')
    print('            remote: %s --loglevel debug --hardware default --listen 2201' % sys.argv[0])
    print('            local:  %s --loglevel debug --hardware 192.168.1.2:2201' % sys.argv[0])
    print()

def show_usage_and_exit():
    '''Show information on command line arguments and exit with error'''
    print()
    usage()
    sys.exit(2)
  
def parse_address_port(address):
    '''Parse a string with IP address and optional port into its parts'''
    try:
        try:
            ip = ip_address(address)
            port = 2201
        except ValueError:
            parsed = urlparse('//{}'.format(address))
            ip = ip_address(parsed.hostname)
            port = parsed.port
        return ip, port
    except ValueError:
        return None, None

def parse_opts():
    '''Check and parse the command line arguments'''
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'g:h:l:?', ['help', 'gui=', 'hardware=', 'listen=', 'loglevel='])
    except getopt.GetoptError as ex:
        print('invalid command line argument(s)')
        show_usage_and_exit()
    gui = 'auto'
    hardware = 'demo'
    listen_address = '0.0.0.0'
    listen_port = None
    remote_address = None
    remote_port = None
    loglevel=logging.INFO
    for o, a in opts:
        if o in ('-?', '--help'):
            usage()
            sys.exit()
        elif o in ('-g', '--gui'):
            a = a.lower()
            if a in ['no', 'auto', 'yes']:
                gui = a
            else:
                print('invalid GUI argument specified')
                show_usage_and_exit()                
        elif o in ('-h', '--hardware'):
            if a in ['default', 'demo', 'didacta', 'ftduino']:
                hardware = a
            elif ('.' in a) or (':' in a):
                remote_address, remote_port = parse_address_port(a)
                if remote_address is None:
                    print('invalid remote address specified as <hardware>')
                    show_usage_and_exit()                
            else:
                print('invalid hardware specified')
                show_usage_and_exit()                
        elif o in ('-l', '--listen'):
            a = a.split(':')
            if (len(a)>2) or ((len(a)==2) and not a[1].isdigit()):
                print('invalid address/port for listen')
                show_usage_and_exit()
            elif len(a) == 1:
                listen_port = a[0]
                if not listen_port.isdigit():
                    print('no port or invalid port given for listen')
                    show_usage_and_exit()
            else:
                listen_address, listen_port = a
        elif o in ('--loglevel'):
            a = a.lower()
            if a == 'debug':
              loglevel = logging.DEBUG
            elif a == 'info':
              loglevel = logging.INFO
            elif a == 'error':
              loglevel = logging.ERROR
            else:
                print('invalid loglevel')
                show_usage_and_exit()
        else:
            assert False, 'unhandled option'
    if len(args) > 0:
        print('invalid argument')
        show_usage_and_exit
    if listen_port is None:
        listen_address_port = None
    else:
        listen_address_port = listen_address + ':' + listen_port
    if (listen_address_port is not None) and (remote_address is not None):
        print('remote hardware and listen address/port must not be provided at the same time')
        show_usage_and_exit
    if gui == 'no':
        gui = False
    elif gui == 'yes':
        gui = True
    else: # 'auto'
        gui = (listen_address_port is None)
    return gui, hardware, remote_address, remote_port, listen_address_port, loglevel

def main():
    '''Main function'''
    # CLI argument parsing
    gui, hwname, remote_address, remote_port, listen_address_port, loglevel = parse_opts()
    # Basic logging configuration
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s', level=loglevel)
    # Common modules
    hwlist = []
    mod_listener = None
    if remote_address is not None:
        # Remote device (note: this can only be used with Python >= 3.5 and will fail with an exception with older versions)
        if sys.version_info >= (3, 5): # the following import is not compatible with older Python versions
            from .hardware import remote
            hwlist.append(remote.HardwareRemote(remote_address, remote_port)) # requires Python >= 3.5
        else:
            logger.error('Python version is too old, you need 3.5 or higher')
            exit(1)
    else:
        # Local device/hardware
        if hwname == 'demo':
            from .hardware import demo
            hwlist.append(demo.HardwareDemo())
        elif hwname == 'default':
            from .hardware import motorhat
            hwlist.append(motorhat.HardwareMotorHat())
            from .hardware import builtingpio
            hwlist.append(builtingpio.HardwareBuiltinGPIO())
        elif hwname == 'didacta':
            from .hardware import didacta
            hwlist.append(didacta.HardwareDidacta())
        elif hwname == 'ftduino':
            from .hardware import ftduino
            hwlist.append(ftduino.HardwareFtDuino())
    if listen_address_port is not None:
        # Listner (note: this can only be used with Python >= 3.5 and will fail with an exception with older versions)
        if sys.version_info >= (3, 5): # the following import is not compatible with older Python versions
            from . import listener
            mod_listener = listener.Listener(listen_address_port) # requires Python >= 3.5
        else:
            logger.error('Python version is too old, you need 3.5 or higher')
            exit(1)
    # Event loop with needed modules
    if gui:
        from .eventprocessor import tk
        eventloop = tk.EventProcessorTk()
    else:
        from .eventprocessor import standalone
        eventloop = standalone.EventProcessorStandalone()
    for hw in hwlist:
        eventloop.register_module(hw)
    eventloop.register_module(mod_listener)
    if gui: # user code module only needed with GUI
        from . import usercode
        mod_user = usercode.UserCode()
        eventloop.register_module(mod_user)
    eventloop.run()
    if gui:
        mod_user.stop_code() # make sure that the thread running code gets stopped
