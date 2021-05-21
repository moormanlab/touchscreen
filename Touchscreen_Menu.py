#!/usr/bin/python3
import pygame, pygame_menu
import logging
import os, subprocess
from importlib import import_module
from importlib import reload as reload_module
import inspect
import datetime
import time
import tinydb

import showip
from keyboard import keyboard
from return_to_menu import return_to_menu
from hal import isRaspberryPI, Valve, IRSensor, Buzzer

logger = logging.getLogger('TouchMenu')
logPath = os.path.abspath('logs')
protocolsPath = 'protocols'
userLogHdlr = None
touchDBFile = 'touchDB.json'

SCREENWIDTH  = 800
SCREENHEIGHT = 480


def back_button(menu):
    menu.add.vertical_margin(30)
    menu.add.button('Back', pygame_menu.events.BACK)


def close_button(menu):
    menu.add.vertical_margin(30)
    menu.add.button('Back', pygame_menu.events.CLOSE)


def initialize_menu(title):
    # Creates menu, adding title, and enabling touchscreen mode
    menu = pygame_menu.Menu(title, SCREENWIDTH, SCREENHEIGHT,
                            theme = pygame_menu.themes.THEME_DARK,
                            onclose = pygame_menu.events.RESET,
                            touchscreen = True if isRaspberryPI() else False,
                            joystick_enabled = False,
                            mouse_enabled = False if isRaspberryPI() else True,
                            )

    logger.debug('Menu created: {}'.format(title))
    
    return menu


def import_protocols(filename):
    # Imports file as a module (excludes .py extension)
    try:
        module = import_module(protocolsPath+'.'+filename[:-3])
        #reload_module in case the functions changes while the system is running
        reload_module(module)
        # Retrieves classes from module
        classes = inspect.getmembers(module, inspect.isclass)
    except Exception:
        logger.exception('Exception when importing file {}'.format(filename))
        #TODO add an error message in the screen
        classes = []

    return classes


def protocol_run(protocol, surface, data):

    global userLogHdlr

    logger.debug('Starting protocol {}'.format(protocol.__name__))

    try:
        protoc = protocol(surface, subject = data[0], experimenter = data[1])

        #create new log file for protocol running
        now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
        userLogHdlr.baseFilename = os.path.join(logPath, protocol.__name__+ '_' + now + '.log')

        protoc._init(userLogHdlr)
        protoc._run()
        protoc._end()
        #close protocol logfile
        userLogHdlr.close()
    except Exception:
        logger.exception('Exception running protocol {}'.format(protocol.__name__))
        #TODO add an error message in the screen

    return


def function_menu(filename,data,surface):
    # New function menu
    fMenu = initialize_menu(filename)

    base_classes = ['BaseProtocol', 'Protocol']

    # Get functions from test_file
    protocols = import_protocols(filename)

    # Creates a button for each function
    fMenu.add.label('Subject: {} | Experimenter: {}'.format(data[0],data[1]))
    fMenu.add.vertical_margin(20)
    for protocol in protocols:
        protocol_name, protocol_call = protocol

        if protocol_name in base_classes:
            continue
        else:
            for b in protocol_call.__bases__:
                if b.__name__ in base_classes:
                    fMenu.add.button(protocol_name, protocol_run, protocol_call, surface, data)
                    break

    close_button(fMenu)

    fMenu.mainloop(surface)


def scan_directory(dirPath):
    # Scans directory for relevent python files and returns the file names as an array
    # List of file names in directory
    files = []

    # Goes through each file and checks if they are python files
    for filename in os.listdir(dirPath):
        if filename.endswith('.py'):
            files.append(filename)

    return files


def files_menu(data, surface):
    # Retrieves test files
    files = scan_directory(protocolsPath)
    # Creates new sub menu
    pMenu = initialize_menu('Programs')
    subject = data['subject'][0][0]
    experimenter = data['experimenter'][0][0]
    
    pMenu.add.label('Subject: {} | Experimenter: {}'.format(subject,experimenter))
    pMenu.add.vertical_margin(20)
    for filename in files:
        pMenu.add.button(filename, function_menu, filename, (subject, experimenter), surface)
    
    close_button(pMenu)

    pMenu.mainloop(surface)


def shutdown_pi_menu():

    def shutdown_pi():
        logger.info('Shutting down Raspberry pi')
        time.sleep(.1)
        subprocess.call(['sudo', 'shutdown', 'now'])

    confirm_menu = initialize_menu('Shutdown Device')

    if isRaspberryPI():
        confirm_msg = "Are you sure you want to shutdown your device?"
        confirm_menu.add.label(confirm_msg)
        confirm_menu.add.button('No', pygame_menu.events.BACK)
        confirm_menu.add.button('Yes', shutdown_pi)
    else:
        msg = "Device is not a Raspberry Pi. Cannot shut down."
        confirm_menu.add.label(msg)

    back_button(confirm_menu)

    return confirm_menu


def valve_menu():

    vMenu = initialize_menu('Valve')

    valve = Valve()

    def updateValveStatus(Label,menu):
        state = valve.isOpen()
        otime = valve.getOpenTime()*1000
        if state == True:
            msg = 'Open'
        else:
            msg = 'Closed'
        Label.set_title('State: {:<6} | Drop open time: {:03.0f} ms'.format(msg,otime))

    def increaseOT():
        otime = valve.getOpenTime()
        otime = otime + .01
        valve.setOpenTime(otime)

    def decreaseOT():
        otime = valve.getOpenTime()
        otime = otime - .01
        if otime > 0:
            valve.setOpenTime(otime)

    L1=vMenu.add.label('State:          Drop Open Time:     ms')
    vMenu.add.vertical_margin(20)
    L1.add_draw_callback(updateValveStatus)
    vMenu.add.button('Open Valve', valve.open)
    vMenu.add.button('Close Valve', valve.close)
    vMenu.add.button('Drop Valve', valve.drop)
    frame = vMenu.add.frame_h(400,58)
    frame.pack(vMenu.add.label('Drop Open Time:'))
    frame.pack(vMenu.add.button(' + ', increaseOT,border_width=2))
    frame.pack(vMenu.add._horizontal_margin(20))
    frame.pack(vMenu.add.button('  -  ', decreaseOT,border_width=2))

    back_button(vMenu)

    return vMenu


def ir_menu():

    irMenu = initialize_menu('Infrared Sensor')

    irSensor = IRSensor()

    def updateIRsensor(Label,menu):
        state = irSensor.isPressed()
        if state == True:
            msg = 'Activated'
        else:
            msg = 'Not Activated'
        Label.set_title('IR Sensor state: {:<15}'.format(msg))

    irL1 = irMenu.add.label('Status')
    irL1.add_draw_callback(updateIRsensor)

    irL2 = irMenu.add.label('Last Trigger')
    def sensorTestHandler():
        logger.info('Test Ir Sensor Trigger')
        now = datetime.datetime.now().strftime('%H:%M:%S')
        irL2.set_title('Last Trigger {}'.format(now))

    irSensor.setHandler(sensorTestHandler)

    back_button(irMenu)

    return irMenu


def sound_menu():

    class Params:
        def __init__(self,frec,duration):
            self.frec = frec
            self.duration = duration

    params = Params(440.0,1.0)
    sndMenu = initialize_menu('Sound')

    buzzer = Buzzer()

    def incfrec():
        params.frec = params.frec + 10.0

    def decfrec():
        if params.frec > 20.0:
            params.frec = params.frec - 10.0

    def incduration():
        params.duration = params.duration + 0.1

    def decduration():
        if params.duration > .1:
            params.duration = params.duration - 0.1

    def updateVal(Label,menu):
        Label.set_title('Frequency {:3.0f} Hz | Duration {:2.1f} s'.format(params.frec,params.duration))

    def playsnd():
        buzzer.play(params.frec,params.duration)

    L1=sndMenu.add.label('')
    L1.add_draw_callback(updateVal)
    frameF = sndMenu.add.frame_h(400,58)
    frameF.pack(sndMenu.add.label('Frequency: '))
    frameF.pack(sndMenu.add.button(' + ', incfrec,border_width=2))
    frameF.pack(sndMenu.add._horizontal_margin(20))
    frameF.pack(sndMenu.add.button('  -  ', decfrec,border_width=2))
    frameT = sndMenu.add.frame_h(400,58)
    frameT.pack(sndMenu.add.label('Duration: '))
    frameT.pack(sndMenu.add.button(' + ', incduration,border_width=2))
    frameT.pack(sndMenu.add._horizontal_margin(20))
    frameT.pack(sndMenu.add.button('  -  ', decduration,border_width=2))
    sndMenu.add.button('Play Sound',playsnd)

    back_button(sndMenu)

    return sndMenu


def settings_menu(surface):

    sMenu = initialize_menu('Settings')

    def updateIP(Label, menu):
        Label.set_title('Ip : {}'.format(showip.getip()))

    IPLabel = sMenu.add.label('Ip')
    IPLabel.add_draw_callback(updateIP)
    sMenu.add.vertical_margin(20)

    confirm_menu = shutdown_pi_menu()
    vMenu = valve_menu()
    irMenu = ir_menu()
    sndMenu = sound_menu()
    current_level = logging.getLogger().level
    items = [('Regular', logging.INFO),('Debug', logging.DEBUG)]
    for i in range(len(items)):
        if items[i][1] == current_level:
            current_level_index = i
            break

    def change_loglevel(item,level):
        current = logging.getLogger().level

        if level == current:
            pass
        elif level == logging.DEBUG:
            logging.getLogger().setLevel(level)
            logger.debug('Debug logging mode activated')
        elif level == logging.INFO:
            logger.debug('Debug logging mode deactivated')
            logging.getLogger().setLevel(level)
        else:
            logger.error('Wrong logging level assignment')

    sMenu.add.selector('Logging Level: ',items,onchange=change_loglevel,default=current_level_index)
    sMenu.add.button(vMenu.get_title(),vMenu)
    sMenu.add.button(irMenu.get_title(),irMenu)
    sMenu.add.button(sndMenu.get_title(),sndMenu)
    sMenu.add.vertical_margin(10)
    sMenu.add.button(confirm_menu.get_title(), confirm_menu)

    close_button(sMenu)

    sMenu.mainloop(surface)


def create_surface():
    # Creates surface
    # make fullscreen on touchscreen
    if isRaspberryPI():
        surface = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.FULLSCREEN)
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
    else:
        surface = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    
    return surface



def initialize_logging():
    # Initialize logging 
    formatDate='%Y/%m/%d@@%H:%M:%S'
    sysFormatStr = '%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s'
    sysFormatter = logging.Formatter(fmt=sysFormatStr,datefmt=formatDate)
    userFormatStr = '%(asctime)s.%(msecs)03d@@%(message)s'
    userFormatter = logging.Formatter(fmt=userFormatStr,datefmt=formatDate)

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
    os.makedirs(logPath,exist_ok=True)

    # the delay=1 should prevent the file from being opened until used.
    systemLogFile = os.path.join(logPath, now + '-system.log')
    systemLogHdlr = logging.FileHandler(systemLogFile, mode='w')
    systemLogHdlr.setFormatter(sysFormatter)
    log.addHandler(systemLogHdlr)
    
    global userLogHdlr
    #prepare userLog Handler with dummy log file
    userLogFile = os.path.join('/tmp', now + '-userprotocol.log')
    userLogHdlr = logging.FileHandler(userLogFile, mode='w')
    userLogHdlr.setLevel(logging.INFO)
    userLogHdlr.setFormatter(userFormatter)
    userLogHdlr.close()
    logger.info('Logging initialized')


def dbGetAll(subjectType):

    touchDB = tinydb.TinyDB(touchDBFile)
    table = touchDB.table(subjectType)

    A = table.all()
    nameList = [('No Name',)]
    for item in A:
        nameList.append((item['name'],))
    
    return nameList

def main_menu():
    # Initializes pygame and logging
    pygame.init()
    initialize_logging()

    logger.debug('Running in Raspberry PI = {}'.format(isRaspberryPI()))
    
    # Creates surface based on machine
    surface = create_surface()
    
    menu = initialize_menu('Mouse Touchscreen Menu')

    def addItems(selector, surface):
        subject = keyboard(surface)
        sType = selector.get_id()

        if subject != '':
            #global subjectss
            touchDB = tinydb.TinyDB(touchDBFile)
            table = touchDB.table(sType)
            if table.search(tinydb.Query().name==subject):
                print('already there')
            else:
                table.insert({'name':subject})
                items = selector._items
                items.append((subject,))
                selector.update_items(items)
                selector.make_selection_drop()
                selector._index = len(items) -1

    def delItems(selector):
        sType = selector.get_id()
        touchDB = tinydb.TinyDB(touchDBFile)
        table = touchDB.table(sType)
        sValue = selector.get_value()
        subject = sValue[0][0]
        if subject != 'No Name':
            print('to remove {}'.format(subject))
            table.remove(tinydb.Query().name==subject)
            items = selector._items
            items.pop(items.index(sValue[0]))
            selector._index = 0
            selector.update_items(items)
            selector.make_selection_drop()

    def clearItems(selector):
        sType = selector.get_id()
        touchDB = tinydb.TinyDB(touchDBFile)
        table = touchDB.table(sType)
        table.truncate()
        items = [('No Name',)]
        selector._index = 0
        selector.update_items(items)
        selector.make_selection_drop()

    def run_files_menu(menu, surface):
        data = menu.get_input_data()
        files_menu(data, surface)

    # Creates initial buttons
    frameS = menu.add.frame_h(700,58)
    S1 = menu.add.dropselect('Subject Id', items=dbGetAll('subject'), default=0, dropselect_id='subject', placeholder='Select        ', placeholder_add_to_selection_box = False)
    frameS.pack(menu.add.button('Clear', clearItems, S1), align='align-right')
    frameS.pack(menu.add.button('Del', delItems, S1), align='align-right')
    frameS.pack(menu.add.button('Add', addItems, S1, surface), align='align-right')
    frameS.pack(S1, align='align-right')

    frameE = menu.add.frame_h(700,58)
    S2 = menu.add.dropselect('Experimenter Id', items=dbGetAll('experimenter'), default=0, dropselect_id='experimenter', placeholder='Select        ', placeholder_add_to_selection_box = False) 
    frameE.pack(menu.add.button('Clear', clearItems, S2), align='align-right')
    frameE.pack(menu.add.button('Del', delItems, S2), align='align-right')
    frameE.pack(menu.add.button('Add', addItems, S2, surface), align='align-right')
    frameE.pack(S2, align='align-right')

    menu.add.vertical_margin(30)
    menu.add.button('Protocols', run_files_menu, menu, surface)
    menu.add.vertical_margin(40)
    menu.add.button('Settings', settings_menu,surface)

    # Allows menu to be run
    menu.mainloop(surface)

    logger.info('Exiting Menu')

    return

if __name__ == "__main__":
    main_menu()
    
