#!/usr/bin/python3
import pygame
import pygame_menu
from hal import isRaspberryPI
import logging

# Initialize logging 
logging.basicConfig(filename ='test.log', level= logging.INFO, filemode='w+', 
        datefmt='%Y/%m/%d@@%H:%M:%S',
        format='%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s')

logging.getLogger('TouchMenu')

#colors
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
black = (0,0,0)
yellow = (255,255,0)
purple = (255,0,255)
white = (255,255,255)
deepskyblue = (0,191,255)
gray = (128,128,128)

# Initializes pygame
pygame.init()

#Creates surface width=800, height=400
#make fullscreen on touchscreen
if isRaspberryPI():
    surface = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
    pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
else:
    surface = pygame.display.set_mode((800,480))

# Creates menu, adding title, and enabling touchscreen mode
menu = pygame_menu.Menu('Mouse Touchscreen Menu',800,480, 
                        theme=pygame_menu.themes.THEME_GREEN, 
                        onclose=pygame_menu.events.RESET,
                        touchscreen=True if isRaspberryPI() else False,
                        joystick_enabled=False,
                        mouse_enabled = False if isRaspberryPI() else True)

# Importing Jason's behavioral test script
import mouse_touchscreen
menu.add.button('Classical Conditioning', mouse_touchscreen.classicalConditioning, surface)

menu.add.button('Operant Conditioning', mouse_touchscreen.operantConditioning, surface)

menu.add.button('Behavioral Test 1', mouse_touchscreen.behavioral_test_1, surface)

# Allows menu to be run
menu.mainloop(surface)
