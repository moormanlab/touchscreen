import pygame, logging, subprocess, tinydb, inspect, importlib, os, datetime, queue, psutil, sys
from utils.utils import (
    create_surface, 
    touchDBFile, 
    protocolsPath, 
    logPath, 
    initialize_hardware, 
    initialize_logging, 
    scan_directory, 
    database_init,
    initialize_menu, 
    formatDate,
    close_IRSensor_thread,
    get_database
)
from utils import utils
from hardware.hal import isRaspberryPI, IRSensor
from utils.BackgroundClient import BackgroundClient, ClientManager


logger = logging.getLogger('TouchClient')




def protocol_run(protocol, surface, data, client):
    """create and run the protocol"""
    logger.debug('Starting protocol {}'.format(protocol.__name__))
    initialize_hardware()

    try:
        protoc = protocol(surface, subject=data[0], experimenter=data[1])
        # create new log file for protocol running
        now = datetime.datetime.now().strftime('%Y%m%d-%H%M') # get date for protocol log file
        userFormatStr = '%(asctime)s.%(msecs)03d@@%(message)s'
        userFormatter = logging.Formatter(fmt=userFormatStr, datefmt=formatDate) 
        userLogFile = os.path.join(logPath, protocol.__name__ + '_' + now + '.log')
        userLogHdlr = logging.FileHandler(userLogFile, mode='w') # create protocol log handler
        userLogHdlr.setLevel(logging.INFO)
        userLogHdlr.setFormatter(userFormatter)
        userLogHdlr.close()

        utils.RUNNING_PROTOCOL = protoc # reference so that the event thread can call quit method
        client.sync_status('running %s' % type(protoc).__name__)
        protoc._init(userLogHdlr)
        protoc._run()
        protoc._end()

    except Exception as e:
        msg = 'Exception running protocol \'{}\'. Check logfile to see details'.format(protocol.__name__)
        logger.exception('Exception running protocol {}'.format(protocol.__name__))

    finally:
        utils.RUNNING_PROTOCOL = None
        client.sync_status(None)

def import_protocols(filename):
    """try importing protocol"""
    try:
        module = importlib.import_module(protocolsPath + '.' + filename[:-3])
        # reload module in case the functions changes while the system is running
        importlib.reload(module)
        # Retrieves classes from module
        all_classes = inspect.getmembers(module, inspect.isclass)
        bases = ('Protocol')
        classes = [protocol for protocol in all_classes if protocol[0] not in bases] # only accept Protocol, not BaseProtocol
    except Exception as e:
        msg = 'Exception when importing file: {}. Check logfile to see details'.format(filename)
        logger.exception('Exception when importing file {}'.format(filename))
        # sio.emit('import_exception', {'message': msg, 'exception': e})
        classes = []
    return classes


def handle_protocol(surface, data, client):
    """run protocol if it exists locally"""
    protocols = import_protocols(data.get('filename'))
    for proto in protocols:
        if proto[0] == data.get('protocol'):
            for base in proto[1].__bases__:
                if base.__name__ == 'Protocol':
                    protocol_run(proto[1], surface, (data.get('subject'), data.get('experimenter')), client)
                    return
def shutdown():
    if isRaspberryPI():
        logger.info('Shutting down Raspberry pi')
        subprocess.call(['sudo', 'sync'])
        time.sleep(1)
        subprocess.call(['sudo', 'shutdown', '-h', 'now'])
def restart(client):
    if isRaspberryPI():
        client.sync_status('Rebooting Device')
        logger.info('Restarting Raspberry pi')
        subprocess.call(['sudo', 'sync'])
        time.sleep(1)
        subprocess.call(['sudo', 'shutdown', '-r', 'now'])
def update(client):
    if isRaspberryPI():
        client.sync_status('Updating Device')
        ret = subprocess.call(['scripts/update.sh'])
        if ret == 0:
            logger.info('Successfully updated software, restarting application')
            restart()
        else:
            logger.error(f'Failed to update software with status code: {ret}')

def menu_mode():
    utils.EXIT = True
    utils.RELOAD = True
def quit():
    utils.EXIT = True
    utils.RELOAD = False
def no_event(event):
    logger.error(f'No event: {event}')
def run(surface, data, client):
    """delegate the event"""
    # note that the 'stop' event is handled in the EventClient thread
    events = {
        'run': {'function': handle_protocol, 'args': (surface, data, client)},
        'quit': {'function': quit},
        'menu': {'function': menu_mode},
        'update': {'function': update, 'args': (client,)},
        'shutdown': {'function': shutdown},
        'restart': {'function': restart, 'args': (client,)}
    }
    event = events.get(data.get('event'), {'function': no_event, 'args': (data.get('event'),)})
    event.get('function')(*event.get('args',()), **event.get('kwargs', {}))

def main_menu():
    utils.EXIT = False
    utils.RELOAD = True
    pygame.init()
    logger.debug('Running in Raspberry PI = {}'.format(isRaspberryPI()))
    logger.info('running in Client mode')
    surface = create_surface()
    menu = initialize_menu('Mouse Touchscreen Client')
    q = queue.Queue()
    client = ClientManager(q)
    utils.EXIT = client.start()



    def check_exit():
        if utils.EXIT:
            logger.info('restarting in Menu mode')
            menu.disable()
    def worker():
        """retrieve tasks from queue and take run it"""
        try:
           data = q.get_nowait()
        except queue.Empty:
            pass 
        else:
            run(surface, data, client)
            q.task_done()

    def bg_tasks():
        check_exit()
        worker()
    #test_run(surface)
    # Allows menu to be run
    try:
        menu.mainloop(surface, bgfun=bg_tasks, fps_limit=30)
    except Exception:
        logger.exception('Exception running mainloop')
    client.join()
    logger.info('Exiting Client')

    return utils.RELOAD

if __name__ == '__main__':
    database_init()
    initialize_logging()
    main_menu()
    close_IRSensor_thread()