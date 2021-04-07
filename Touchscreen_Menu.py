#!/usr/bin/python3
import pygame, pygame_menu
from hal import isRaspberryPI
import logging
# Importing Jason's behavioral test script
import mouse_touchscreen
import showip
import os
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

def function_menu(test_file):
    # New function menu
    menu, surface = initialize_menu()

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

    # Allows menu to be run
    menu.mainloop(surface)
        

def file_menu():
    # Retrieves test files
    test_files = scan_directory()
    # Creates new sub menu
    menu, surface = initialize_menu()
    
    for files in test_files:
        menu.add.button(files, function_menu, files)

    # Allows menu to be run
    menu.mainloop(surface)


def initialize_logging():
    # Initialize logging 
    logging.basicConfig(filename ='test.log', level= logging.INFO, filemode='w+', 
                        datefmt='%Y/%m/%d@@%H:%M:%S',
                        format='%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s')

    logging.getLogger('TouchMenu')


def create_surface():
    # Creates surface width=800, height=400
    # make fullscreen on touchscreen
    surface = pygame.display.set_mode((800,480))

    if isRaspberryPI():
        surface = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
    
    return surface


def initial_buttons(menu, surface):
    #menu.add.button('Classical Conditioning', mouse_touchscreen.classicalConditioning, surface)
    #menu.add.button('Operant Conditioning', mouse_touchscreen.operantConditioning, surface)
    #menu.add.button('Behavioral Test 1', mouse_touchscreen.behavioral_test_1, surface)
    menu.add.button('Programs', file_menu)
    return menu


def initialize_menu():
    # Initializes pygame and logging
    pygame.init()
    initialize_logging()
    
    # Creates surface based on machine
    surface = create_surface()

    # Creates menu, adding title, and enabling touchscreen mode
    menu = pygame_menu.Menu('Mouse Touchscreen Menu', 800,480,
                            theme=pygame_menu.themes.THEME_GREEN, 
                            onclose=pygame_menu.events.RESET,
                            touchscreen=True if isRaspberryPI() else False,
                            joystick_enabled=False,
                            mouse_enabled = False if isRaspberryPI() else True)

    return (menu, surface)


def main():
    # Start menu
    menu, surface = initialize_menu()
    # Adds IP labels
    IPLabel = menu.add.label('Ip : ' + showip.getip())
    IPLabel.add_draw_callback(updateIP)
    # Creates initial buttons
    initial_buttons(menu, surface)

    # Allows menu to be run
    menu.mainloop(surface)


if __name__ == "__main__":
    main()