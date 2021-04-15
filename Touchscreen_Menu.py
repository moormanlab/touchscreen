#!/usr/bin/python3
import pygame, pygame_menu
from hal import isRaspberryPI, Valve
import logging
import showip
import os, subprocess
from importlib import import_module
import inspect

def updateIP(Label, menu):
    Label.set_title('Ip : ' + showip.getip())

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
        
def shutdown_pi(confirm_menu):
    shut_down = ["shutdown", "-f", "-s", "-t", "10"]

    if isRaspberryPI():
        confirm_msg = "Are you sure you want to shutdown your device?"
        confirm_menu.add.label(confirm_msg)
        confirm_menu.add.button('No', pygame_menu.events.BACK)
        confirm_menu.add.button('Yes', subprocess.call, shut_down)
    else:
        msg = "Device is not a Raspberry Pi. Cannot shut down."
        confirm_menu.add.label(msg)



def settings_menu():

    sMenu = initialize_menu('Settings')

    IPLabel = sMenu.add.label('Ip : ' + showip.getip())
    IPLabel.add_draw_callback(updateIP)

    vMenu = initialize_menu('Valve')
    confirm_menu = initialize_menu('')

    sMenu.add.button(vMenu.get_title(),vMenu)
    sMenu.add.button('Shutdown device', confirm_menu)

    shutdown_pi(confirm_menu)

    val = Valve()
    vMenu.add.button('Open Valve', val.open)
    vMenu.add.button('Close Valve', val.close)
    vMenu.add.button('Drop Valve', val.drop)

    return sMenu


def file_menu(surface):
    # Retrieves test files
    test_files = scan_directory()
    # Creates new sub menu
    pMenu = initialize_menu('Programs')
    
    for files in test_files:
        fmenu = function_menu(files,surface)
        pMenu.add.button(files, fmenu)

    return pMenu


def initialize_logging():
    # Initialize logging 
    import datetime
    now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
    os.makedirs('logs',exist_ok=True)
    logfile = 'logs/' + now + '.log'
    logging.basicConfig(filename =logfile, level= logging.INFO, filemode='w+',
                        datefmt='%Y/%m/%d@@%H:%M:%S',
                        format='%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s')

    logging.getLogger('TouchMenu')


def create_surface():
    # Creates surface width=800, height=480
    # make fullscreen on touchscreen
    if isRaspberryPI():
        surface = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
    else:
        surface = pygame.display.set_mode((800,480))
    
    return surface


def initial_buttons(menu, surface):
    hMenu = settings_menu()
    fMenu = file_menu(surface)

    menu.add.button(hMenu.get_title(), hMenu)
    menu.add.button(fMenu.get_title(), fMenu, surface)


def initialize_menu(title, main_menu=False):
    # Creates menu, adding title, and enabling touchscreen mode
    menu = pygame_menu.Menu(title, 800,480,
                            theme=pygame_menu.themes.THEME_GREEN, 
                            onclose=pygame_menu.events.RESET,
                            touchscreen=True if isRaspberryPI() else False,
                            joystick_enabled=False,
                            mouse_enabled = False if isRaspberryPI() else True)
    
    if main_menu is False:
        menu.add.button('Back', pygame_menu.events.BACK)
        menu.add.vertical_margin(40)

    return menu


def main():
    # Initializes pygame and logging
    pygame.init()
    
    # Start menu
    initialize_logging()
    # Creates surface based on machine
    surface = create_surface()

    menu = initialize_menu('Mouse Touchscreen Menu', main_menu=True)

    # Creates initial buttons
    initial_buttons(menu, surface)

    # Allows menu to be run
    menu.mainloop(surface)


if __name__ == "__main__":
    main()
