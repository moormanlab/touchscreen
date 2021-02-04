'''
Mouse Touchscreen Program, Moorman Lab 2020 
Code written by Jason Biundo, version 1.1 10/2020

This program utilizes the pygame library to create an interactive program that mice can 
interact with on a touchscreen that is run by a Raspberry pi. This program is designed to 
eventually be generalizable to a variety of different tasks.
'''

# Import and initialize the pygame library
import pygame
from time import sleep
import logging 
import io
import os
from hal import Buzzer, IRSensor, Valve, isRaspberryPI

pygame.init()
pygame.display.set_caption('Mouse Touchscreen Program')

buzz = Buzzer()

def sensorHandler():
    print('Decide what to do when the IRbeam was broken')

sensor = IRSensor(sensorHandler)

valve = Valve()

#Initialize logging 
logging.basicConfig(filename ='test.log', level= logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
#format='%(asctime)s:%(levelname)s:%(message)s'

# Import pygame.locals for easier access to key coordinates
from pygame.locals import (
    K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT,
)

#colors
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
black = (0,0,0)
yellow = (255,255,0)
purple = (255,0,255)
white = (255,255,255)
deepskyblue = (0,191,255)



#sound effects - uncomment if you have the sound file 
#effect = pygame.mixer.Sound('chime.wav')

#Functions to add
''' 
- Add shapes (one function for each shape most likely, i.e circle, square, polygon)
- Check collison 
- Update screen?
-Play sound 
'''

# Set up the display window. Touchscreen dimensions = 800x400
screen_width = 800 
screen_height = 400
screen = pygame.display.set_mode([screen_width, screen_height])
logging.info('Program Started')

#make fullscreen on touchscreen
if isRaspberryPI():
    screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN)

# Function to check collision of mouse with shape 
def check_collision(object, mouse_pos, left_click, color=(0,0,0)):
    if object.collidepoint(mouse_pos) and left_click:
        '''
        Function to check if mouse click collides with one of the objects. 
        Takes in object, mouse position (tuple of coordinates) and pressed (boolean, True if mouse was clicked)
        Default argument for color is black, but can be changed. 
        '''
        print('You pressed', object)
        screen.fill(color)
        #effect.play() #plays sound if uncommented
        pygame.display.flip()
        pygame.mouse.set_pos(0,0)
        buzz.play()
        valve.drop()
        #if IS_RASPBERRY_PI == True:
        #    bz.play(Tone(440.0))
        #pygame.time.wait(1000) #pauses program for 1000ms for flash
        #    bz.stop()
        logging.info('Shape: {}'.format(object))


print('Running in Raspberry PI = {}'.format(isRaspberryPI()))

running = True
off = False 

# Main loop, run until the user asks to quit
while running:
    #turn on/off visibility of mouse cursor (True=visible, False=hidden)
    #Turns visibility off if Raspberry pi is connected
    if isRaspberryPI():
        pygame.mouse.set_visible(off)
    
    #draw test shapes
    obj1= pygame.draw.circle(screen, yellow, (75,250), 57)
    obj2= pygame.draw.circle(screen, purple , (260, 250), 57)
    obj3 = pygame.draw.rect(screen, red, (400,200, 100,100))
    obj4 = pygame.draw.rect(screen, blue, (600,200, 125,100))
    objList = [obj1,obj2,obj3,obj4]
    
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        #check for mousebutton 
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos= pygame.mouse.get_pos()
            print('The position of the cursor is', mouse_pos)
            logging.info('Coordinates:' + str(mouse_pos))


        #mouse_pos = pygame.mouse.get_pos()
        left_click, pressed2, right_click = pygame.mouse.get_pressed() #pressed 1 is left click, pressed 3 is right click 
        
        # Check if the object "collided" with the mouse pos and if the left mouse button was pressed
        check_collision(obj1,mouse_pos,left_click, yellow)
        check_collision(obj2,mouse_pos,left_click, purple)
        check_collision(obj3,mouse_pos,left_click, red)
        check_collision(obj4,mouse_pos,left_click, blue)
        # for obj in objList:
        #     check_collision(obj,mouse_pos,left_click,white)

        #escape from program
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False
            # elif event.key == K_UP:
            #     screen = pygame.display.set_mode([screen_width, screen_height],pygame.FULLSCREEN)
        elif event.type == pygame.QUIT:
                running = False
            
    # Fill the background with black
    screen.fill(black)
    # Draw circles
    pygame.draw.circle(screen, purple, (260, 250), 57)
    pygame.draw.circle(screen, yellow, (75,250), 57)
    #Draw squares
    pygame.draw.rect(screen, red, (400,200, 100,100))
    pygame.draw.rect(screen, blue, (600,200, 125,100))

    if isRaspberryPI():
        pygame.mouse.set_pos(0,0)
        
    #Reset mouse position every loop to avoid problems with touchscreens. Comment this if using a computer
    #pygame.mouse.set_pos(0,0)

    # Update  the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()



# Check if the object "collided" with the mouse pos and if the left mouse button was pressed
        # if circ1.collidepoint(mouse_pos) and left_click:
        #     print('You pressed the circle')
        #     screen.fill(purple)
        #     pygame.display.flip()
        #     effect.play()
        #     time.sleep(1)
        #     pygame.mouse.set_pos(0,0)
#         if rec1.collidepoint(mouse_pos) and left_click:
#             print('You pressed the square')
#             screen.fill(red)
#             pygame.display.flip()
#             pygame.mouse.set_pos(0,0)
#             effect.play()
#             time.sleep(.5)
#         if circ2.collidepoint(mouse_pos) and left_click:
#             print('You pressed the yellow circle')
#             screen.fill(yellow)
#             pygame.display.flip()
#             pygame.mouse.set_pos(0,0)
#             effect.play()
#             time.sleep(.5)
#         if rec2.collidepoint(mouse_pos) and left_click:
#             print('You pressed the rectangle')
#             screen.fill(blue)
#             pygame.display.flip()
#             pygame.mouse.set_pos(0,0)
#             effect.play()
#             time.sleep(.5)
