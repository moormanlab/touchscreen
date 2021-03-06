#!/usr/bin/python3
import pygame
import pygame_menu
# Importing Jason's behavioral test script
import mouse_touchscreen
from hal import isRaspberryPI

#colors
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
black = (0,0,0)
yellow = (255,255,0)
purple = (255,0,255)
white = (255,255,255)
deepskyblue = (0,191,255)

# Initializes pygame
pygame.init()

#Creates surface width=800, height=400
    #make fullscreen on touchscreen
if isRaspberryPI():
    surface = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
else:
    surface = pygame.display.set_mode((800,480))

# Creates menu, adding title, and enabling touchscreen mode
menu = pygame_menu.Menu(480,800,'Mouse Touchscreen Menu', 
                        theme=pygame_menu.themes.THEME_GREEN, 
                        onclose=pygame_menu.events.RESET,
                        touchscreen_enabled=True,
                        joystick_enabled=False,
                        mouse_enabled =False if isRaspberryPI() else True)

# Creates button for behavioral test 1
# Uses Jason's behavioral test script
menu.add_button('Behavioral Test 1', mouse_touchscreen.behavioral_test_1)

# def behavioral_test_2():
#     print('test 2 placeholder')

menu.add_button('Behavioral Test 2', mouse_touchscreen.behavioral_test_2)

def behavioral_test_3():
    print('test 3 placeholder')

menu.add_button('Behavioral Test 3', behavioral_test_3)

# Allows menu to be run
menu.mainloop(surface)

