#!/usr/bin/python3
import pygame, pygame_menu
from hal import isRaspberryPI, Valve, IRSensor, Buzzer
import logging
import showip
import os, subprocess
from importlib import import_module
from importlib import reload as reload_module
import inspect
import datetime
import pygame_vkeyboard as vkboard
from return_to_menu import return_to_menu
from fontTools.ttLib import TTFont

logger = logging.getLogger('TouchMenu')

def back_button(menu):
    menu.add.vertical_margin(30)
    menu.add.button('Back', pygame_menu.events.BACK)

def close_button(menu):
    menu.add.vertical_margin(30)
    menu.add.button('Back', pygame_menu.events.CLOSE)

# Scans directory for relevent python files and returns the file names as an array
def scan_directory():
    # List of file names in directory
    test_files = []

    # Goes through each file and checks if they are python files
    for files in os.listdir('protocols'):
        if files.endswith('.py'):
            test_files.append(files)

    return test_files

def import_tests(test_file):
    # Imports test file as a module (excludes .py extension)
    module = import_module('protocols.'+test_file[:-3])
    #reload_module in case the functions changes while the system is running
    reload_module(module)
    # Retrieves functions from module
    functions = inspect.getmembers(module, inspect.isclass)
    return functions


def protocol_run(protocol,surface):

    protoc = protocol(surface)
    protoc._init()
    protoc._run()
    protoc._end()

    return


def function_menu(test_file,surface):
    # New function menu
    fmenu = initialize_menu(test_file)

    exclude_classes = ['BaseProtocol', 'Protocol']

    # Get functions from test_file
    protocols = import_tests(test_file)

    # Creates a button for each function
    for protocol in protocols:
        protocol_name, protocol_call = protocol

        if protocol_name in exclude_classes:
            continue
        else:
            fmenu.add.button(protocol_name, protocol_run, protocol_call, surface)

    close_button(fmenu)

    fmenu.mainloop(surface)
        

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

    confirm_menu = shutdown_pi()
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
        pMenu.add.button(files, function_menu, files, surface)
    
    close_button(pMenu)

    pMenu.mainloop(surface)


def subject_ID():
    screen = create_surface()
    screen.fill((20, 100, 100))

    # Create keyboard
    keys = ['1234567890','qwertyuiop','asdfghjkl','.-zxcvbnm_/']
    layout = vkboard.VKeyboardLayout(keys, allow_special_chars=False)
    keyboard = vkboard.VKeyboard(screen,
                                 on_key_event,
                                 layout,
                                 renderer=vkboard.VKeyboardRenderer.DARK,
                                 show_text=True,
                                 joystick_navigation=True)

    font = pygame.font.Font('DejaVuSans.ttf', 40)
    enter_text = 'Enter'
    text = font.render(enter_text,True, (182, 183, 184), (59, 56, 54))
    enter_key = text.get_rect()
    enter_key.topleft = (670,320)
    #outline = pygame.draw.rect(text, (124, 183, 62), enter_key,3)

    running = True

    # Main loop
    while running:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                enter_pressed = enter_key.collidepoint(pygame.mouse.get_pos())
                if enter_pressed:
                    text = font.render('Enter', True, (255,255,255), (47,48,51))
                    input = keyboard.get_text()
                    print(input)
                    subject_logging(input)

            else:
                text = font.render('Enter', True, (182, 183, 184), (59, 56, 54))


            running = not return_to_menu(event,screen, color = (20, 100, 100))

        keyboard.update(events)
        rects = keyboard.draw(screen)

        screen.blit(text, enter_key)
        pygame.display.update(rects)
        pygame.display.update(enter_key)
        #pygame.display.update(outline)
    
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
    menu.add.button('Subject ID', subject_ID)
    menu.add.button('Protocols',file_menu, surface)
    menu.add.vertical_margin(40)
    menu.add.button('Settings', settings_menu,surface)


def initialize_menu(title):
    # Creates menu, adding title, and enabling touchscreen mode
    menu = pygame_menu.Menu(title, 800,480,
                            theme=pygame_menu.themes.THEME_DARK,
                            onclose=pygame_menu.events.RESET,
                            touchscreen=True if isRaspberryPI() else False,
                            joystick_enabled=False,
                            mouse_enabled = False if isRaspberryPI() else True)
    
    return menu

def on_key_event(text):
    """ Print the current text. """
    print('Current text:', text)

def main():
    # Initializes pygame and logging
    pygame.init()
    initialize_logging()

    logger.debug('Running in Raspberry PI = {}'.format(isRaspberryPI()))
    
    # Creates surface based on machine
    surface = create_surface()
    
    menu = initialize_menu('Mouse Touchscreen Menu')

    # Creates initial buttons
    initial_buttons(menu, surface)

    # Allows menu to be run
    menu.mainloop(surface)


if __name__ == "__main__":
    main()
    
