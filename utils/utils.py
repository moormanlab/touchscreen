import pygame, pygame_menu
import os
import logging
import tinydb
import datetime
import uuid

from hardware.hal import isRaspberryPI, LiqReward, IRSensor, Sound, Battery


logger = logging.getLogger('utils')
SCREENWIDTH  = 800
SCREENHEIGHT = 480

POINTERPRESSED = 1
POINTERMOTION = 2
POINTERRELEASED = 3

tsColors = {
        'red':         ( 255,   0,   0),
        'green':       (   0, 255,   0),
        'blue':        (   0,   0, 255),
        'black':       (   0,   0,   0),
        'yellow':      ( 255, 255,   0),
        'purple':      ( 255,   0, 255),
        'white':       ( 255, 255, 255),
        'deepskyblue': (   0, 191, 255),
        'gray':        ( 128, 128, 128),
        'darkgray':    (  64,  64,  64),
        }

def getPosition(event):
    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]:
        return event.pos
    elif event.type in [pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP]:
        return(int(event.x*SCREENWIDTH),int(event.y*SCREENHEIGHT))
    return (-1,-1)

##########################
RUNNING_PROTOCOL = None
EXIT = False
RELOAD = False

touchDBFile = 'touchDB.json'
protocolsPath = 'protocols'
logPath = os.path.abspath('logs')
formatDate = '%Y/%m/%d@@%H:%M:%S'

def create_surface():
    # Creates surface
    # make fullscreen on touchscreen
    if isRaspberryPI():
        surface = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.FULLSCREEN)
        pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
    else:
        surface = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

    return surface

def initialize_hardware():
    with get_database() as db:
        table = db.table('settings')

        batteryObj = table.get(tinydb.Query().battery.exists())
        batt = batteryObj['battery']
        if batt:
            battery = Battery()
            if not battery.detect_battery():
                table.update({'battery': False}, doc_ids=[batteryObj.doc_id])

        sensor = table.get(tinydb.Query().rSensor.exists())['rSensor']
        if sensor != 'None':
            irSensor = IRSensor(variant=sensor)

        audio = table.get(tinydb.Query().audio.exists())['audio']
        if audio != 'None':
            sounddev = Sound(audio)

        liquid_reward = table.get(tinydb.Query().lReward.exists())['lReward']
        if liquid_reward != 'None':
            liqrew = LiqReward(variant=liquid_reward)

def scan_directory(dirPath):
    # Scans directory for relevent python files and returns the file names as an array
    # List of file names in directory
    files = []

    # Goes through each file and checks if they are python files
    for filename in os.listdir(dirPath):
        if filename.endswith('.py'):
            files.append(filename)

    files.sort()

    return files

def database_init():
    with get_database() as db:
        table = db.table('settings')
        initOpt = table.get(tinydb.Query().init.exists())

        if not initOpt:
            table.insert({'init': True})
            table.insert({'syncOn': True})
            table.insert({'logDebugOn': True})
            table.insert({'battery': False})
            table.insert({'audio': 'None'})
            table.insert({'rSensor': 'None'})
            table.insert({'lReward': 'None'})
            table.insert({'fReward': 'None'})
            table.insert({'server': 'None'})
            table.insert({'isClient': False})
            table.insert({'id': 'None'})
            table.insert({'password': str(uuid.uuid4())})

def initialize_menu(title):
    # Creates menu, adding title, and enabling touchscreen mode
    menu = pygame_menu.Menu(title, SCREENWIDTH, SCREENHEIGHT,
                            theme=pygame_menu.themes.THEME_DARK,
                            onclose=pygame_menu.events.RESET,
                            touchscreen=True if isRaspberryPI() else False,
                            joystick_enabled=False,
                            mouse_enabled=False if isRaspberryPI() else True,
                            )

    logger.debug('Menu created: {}'.format(title))

    return menu

def initialize_logging():
    if not os.path.isdir(logPath):
        os.mkdir(logPath)
    with get_database() as db:
        table = db.table('settings')
        logOpt = table.get(tinydb.Query().logDebugOn.exists())['logDebugOn']
    #syncOpt = table.get(tinydb.Query().syncOn.exists())['syncOn']

    # if syncOpt:
    #     # wait for time synchronization
    #     msg = piSynchronizeTime()
    # else:
    #     msg = 'Synchronizing time disabled'
    msg = 'Synchronizing time disabled'

    # Initialize logging
    sysFormatStr = '%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s'
    sysFormatter = logging.Formatter(fmt=sysFormatStr, datefmt=formatDate)


    log = logging.getLogger()
    

    if logOpt:
        level = logging.DEBUG
    else:
        level = logging.INFO

    log.setLevel(level)

    now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
    os.makedirs(logPath, exist_ok=True)

    # the delay=1 should prevent the file from being opened until used.
    systemLogFile = os.path.join(logPath, now + '-system.log')
    systemLogHdlr = logging.FileHandler(systemLogFile, mode='w')
    systemLogHdlr.setFormatter(sysFormatter)
    log.addHandler(systemLogHdlr)
 
    logger.info('Logging initialized')
    logger.debug(msg)
    # logger.debug('{}'.format(showip.getip()))

def get_database():
    return tinydb.TinyDB(touchDBFile)
    
def close_IRSensor_thread():
    if not isRaspberryPI():
        IRSensor(variant='sparkfuncustom')._close()