#!/usr/bin/python3
import pygame, pygame_menu
from hal import isRaspberryPI, Valve, IRSensor, Buzzer
import logging
import showip
import os, subprocess
from importlib import import_module
import inspect
import datetime

logger = logging.getLogger('TouchMenu')

# Scans directory for relevent python files and returns the file names as an array
def scan_directory():
    exclude_files = ['Touchscreen_Menu.py', 'hal.py', 'showip.py', 'return_to_menu.py']
    # List of file names in directory
    test_files = []

    # Goes through each file and checks if they are python files
    for files in os.listdir():
        if files.endswith('.py') and files not in exclude_files:
            test_files.append(files)

    return test_files

def import_tests(test_file):
    # Imports test file as a module (excludes .py extension)
    module = import_module(test_file[:-3])
    # Retrieves functions from module
    functions = inspect.getmembers(module, inspect.isfunction)
    return functions

def function_menu(test_file,surface):
    # New function menu
    menu = initialize_menu(test_file)

    exclude_functions = ['return_to_menu', 'isRaspberryPI', 'sensorHandler']

    # Get functions from test_file
    functions = import_tests(test_file)

    # Creates a button for each function
    for function in functions:
        function_name, function_call = function

        if function_name in exclude_functions:
            continue
        # Function has 0 arguments
        elif function_call.__code__.co_argcount == 0:
            menu.add.button(function_name, function_call)
        # Function has 1 argument (assumes Surface is the input)
        else:
            menu.add.button(function_name, function_call, surface)

    return menu
        
def back_button(menu):
    menu.add.vertical_margin(30)
    menu.add.button('Back', pygame_menu.events.BACK)

def shutdown_pi():

    confirm_menu = initialize_menu('Shutdown Device')

    shut_down = ["sudo", "shutdown", "now"]

    if isRaspberryPI():
        confirm_msg = "Are you sure you want to shutdown your device?"
        confirm_menu.add.label(confirm_msg)
        confirm_menu.add.button('No', pygame_menu.events.BACK)
        confirm_menu.add.button('Yes', subprocess.call, shut_down)
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
        params.duration = params.duration + 0.5

    def decduration():
        if params.duration > .5:
            params.duration = params.duration - 0.5

    def updateVal(Label,menu):
        Label.set_title('Frequency {} | Duration {}'.format(params.frec,params.duration))

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

def settings_menu():

    sMenu = initialize_menu('Settings')

    def updateIP(Label, menu):
        Label.set_title('Ip : {}'.format(showip.getip()))

    IPLabel = sMenu.add.label('Ip')
    IPLabel.add_draw_callback(updateIP)
    sMenu.add.vertical_margin(20)

    confirm_menu = shutdown_pi()
    vMenu = valve_menu()
    irMenu = ir_menu()
    sndMenu = sound_menu()

    sMenu.add.button(vMenu.get_title(),vMenu)
    sMenu.add.button(irMenu.get_title(),irMenu)
    sMenu.add.button(sndMenu.get_title(),sndMenu)
    sMenu.add.vertical_margin(10)
    sMenu.add.button(confirm_menu.get_title(), confirm_menu)

    back_button(sMenu)

    return sMenu


def create_surface():
    # Creates surface width=800, height=480
    # make fullscreen on touchscreen
    if isRaspberryPI():
        surface = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
    else:
        surface = pygame.display.set_mode((800,480))
    
    return surface


def file_menu(surface=create_surface()):
    # Retrieves test files
    test_files = scan_directory()
    # Creates new sub menu
    pMenu = initialize_menu('Programs')
    
    for files in test_files:
        func_menu = function_menu(files,surface)
        pMenu.add.button(files, func_menu)
        back_button(func_menu)
    
    back_button(pMenu)

    return pMenu

def subject_logging(input):
    logger = logging.getLogger('SubjectID')
    logger.info('ID: ' + input)


def initialize_logging():
    # Initialize logging 
    now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
    os.makedirs('logs',exist_ok=True)
    logfile = 'logs/' + now + '.log'
    logging.basicConfig(filename =logfile, level= logging.INFO, filemode='w+',
                        datefmt='%Y/%m/%d@@%H:%M:%S',
                        format='%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s')



def initial_buttons(menu, surface):
    hMenu = settings_menu()
    fMenu = file_menu(surface)
    
    menu.add.text_input('Subject ID: ', onreturn=subject_logging)
    menu.add.vertical_margin(40)
    menu.add.button(hMenu.get_title(), hMenu)
    menu.add.button(fMenu.get_title(), fMenu)


def initialize_menu(title):
    # Creates menu, adding title, and enabling touchscreen mode
    menu = pygame_menu.Menu(title, 800,480,
                            theme=pygame_menu.themes.THEME_GREEN, 
                            onclose=pygame_menu.events.RESET,
                            touchscreen=True if isRaspberryPI() else False,
                            joystick_enabled=False,
                            mouse_enabled = False if isRaspberryPI() else True)
    
    return menu


def main():
    # Initializes pygame and logging
    pygame.init()
    initialize_logging()
    
    # Creates surface based on machine
    surface = create_surface()

    menu = initialize_menu('Mouse Touchscreen Menu')

    # Creates initial buttons
    initial_buttons(menu, surface)

    # Allows menu to be run
    menu.mainloop(surface)


if __name__ == "__main__":
    main()
    
