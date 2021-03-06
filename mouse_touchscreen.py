'''
Mouse Touchscreen Program, Moorman Lab 2020 
Code written by Jason Biundo, version 1.1 10/2020

This program utilizes the pygame library to create an interactive program that mice can 
interact with on a touchscreen that is run by a Raspberry pi. This program is designed to 
eventually be generalizable to a variety of different tasks.
'''
import pygame
import time
import logging 
import io
import os
from hal import Buzzer, IRSensor, Valve, isRaspberryPI
#colors
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
black = (0,0,0)
yellow = (255,255,0)
purple = (255,0,255)
white = (255,255,255)
deepskyblue = (0,191,255)



#Functions to add
''' 
- Add shapes (one function for each shape most likely, i.e circle, square, polygon)
- Check collison √
- Update screen?
-Play sound 
'''

# Puts entire script into function to call in menu script
def behavioral_test_1():

    # Import and initialize the pygame library
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
        K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_x
    )
    # Set up the display window. Touchscreen dimensions = 800x400
    screen_width = 800 
    screen_height = 480
    screen = pygame.display.set_mode([screen_width, screen_height])
    logging.info('Program Started')

    #make fullscreen on touchscreen
    if isRaspberryPI():
        screen = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

    def check_collision(objectT, mouse_pos, color=(0,0,0)):
        if objectT.collidepoint(mouse_pos):
            '''
            Function to check if mouse click collides with one of the objects. 
            Takes in object, mouse position (tuple of coordinates) and pressed (boolean, True if mouse was clicked)
            Default argument for color is black, but can be changed. 
            '''
            print('You pressed', objectT)
            screen.fill(color)
            #effect.play() #plays sound if uncommented
            pygame.display.flip()
            pygame.mouse.set_pos(0,0)
            buzz.play()
            pygame.time.wait(1000) #pauses program for 1000ms for flash
            valve.drop()
            logging.info('Shape: {}'.format(objectT))

    print('Running in Raspberry PI = {}'.format(isRaspberryPI()))

    running = True
    off = False 

    # Main loop, run until the user asks to quit
    while running:
        #turn on/off visibility of mouse cursor (True=visible, False=hidden)
        #Turns visibility off if Raspberry pi is connected
        #if isRaspberryPI():
            #pygame.mouse.set_visible(off)
        
        #draw test shapes
        obj1= pygame.draw.circle(screen, yellow, (75,250), 57)
        obj2= pygame.draw.circle(screen, purple , (260, 250), 57)
        obj3 = pygame.draw.rect(screen, red, (400,200, 100,100))
        obj4 = pygame.draw.rect(screen, blue, (600,200, 125,100))
        objList = [obj1,obj2,obj3,obj4]
        
        # Draws invisible box in top right corner to return to menu
        closing_box = pygame.draw.rect(screen, black, (700,0, 100,100))

        mouse_pos = pygame.mouse.get_pos()
	
        eventsToCatch = [pygame.MOUSEBUTTONDOWN, pygame.FINGERUP]
        for event in pygame.event.get():
            #check for mousebutton 
            if event.type == pygame.MOUSEBUTTONDOWN or event.type==pygame.FINGERUP:
                print(event.type)
                mouse_pos= pygame.mouse.get_pos()
                print('The position of the cursor is', mouse_pos)
                logging.info('Coordinates:' + str(mouse_pos))
                left_click, pressed2, right_click = pygame.mouse.get_pressed() #pressed 1 is left click, pressed 3 is right click 
                if left_click or event.type==pygame.FINGERUP:
                    # Check if the object "collided" with the mouse pos and if the left mouse button was pressed
                    check_collision(obj1,mouse_pos, yellow)
                    check_collision(obj2,mouse_pos, purple)
                    check_collision(obj3,mouse_pos, red)
                    check_collision(obj4,mouse_pos, blue)
                    # for obj in objList:
                    #     check_collision(obj,mouse_pos,left_click,white)

            # curs_in_box = False
            # timer = 0
        
            #Event check if statemewtns 
               #escape from program
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    running = False
                # Pressing 'x' key stops behavioral test and returns to menu
                elif event.key == K_x:
                    return 
            elif event.type == pygame.QUIT:
                    running = False
            
            # When mouse is clicked or screen touched, a timer starts
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                timer = time.time()
            # When you unclick mouse or stop touching screen, timer stops

            # Records amount of  time you held mouse button or touched screen
            elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP:
                timer = time.time() - timer
                timer = str(timer)[:5]
                timer = float(timer)
                # Checks if screen was pressed in top right corner
                curs_in_box = closing_box.collidepoint(pygame.mouse.get_pos())
                # Returns to menu if top right corner was pressed for more than 2 seconds
                if curs_in_box and timer > 2:
                    logging.info('Returned to menu')
                    print('User has pressed top right corner for 2 seconds. Returning to menu.')
                    running = False
                    #return      
    
    
        # Fill the background with black
        screen.fill(black)
        # Draw circles
        pygame.draw.circle(screen, purple, (260, 250), 57)
        pygame.draw.circle(screen, yellow, (75,250), 57)
        #Draw squares
        pygame.draw.rect(screen, red, (400,200, 100,100))
        pygame.draw.rect(screen, blue, (600,200, 125,100))

        # Draw invisible closing box
        pygame.draw.rect(screen, black, (700,0, 100,100))

        #if isRaspberryPI():
        #    pygame.mouse.set_pos(0,0)
            
        #Reset mouse position every loop to avoid problems with touchscreens. Comment this if using a computer
        #pygame.mouse.set_pos(0,0)

        # Update  the display
        pygame.display.flip()

    # Done! Time to quit.
    return

def behavioral_test_2():
    # Import and initialize the pygame library
    pygame.display.set_caption('Mouse Touchscreen Program')
    buzz = Buzzer()
    valve = Valve()

    def sensorHandler():
        print('IRbeam was broken')
        buzz.play()
        valve.drop()


    sensor = IRSensor(sensorHandler)

    #Initialize logging 
    logging.basicConfig(filename ='test.log', level= logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    #format='%(asctime)s:%(levelname)s:%(message)s'

    # Import pygame.locals for easier access to key coordinates
    from pygame.locals import (
        K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_x
    )
    # Set up the display window. Touchscreen dimensions = 800x400
    screen_width = 800 
    screen_height = 480
    screen = pygame.display.set_mode([screen_width, screen_height])
    logging.info('Program Started')

    #make fullscreen on touchscreen
    if isRaspberryPI():
        screen = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

    def check_collision(objectT, mouse_pos,color=(0,0,0)):
        if objectT.collidepoint(mouse_pos):
            '''
            Function to check if mouse click collides with one of the objects. 
            Takes in object, mouse position (tuple of coordinates) and pressed (boolean, True if mouse was clicked)
            Default argument for color is black, but can be changed. 
            '''
            print('You pressed', objectT)
            screen.fill(color)
            #effect.play() #plays sound if uncommented
            pygame.display.flip()
            pygame.mouse.set_pos(0,0)
            buzz.play()
            pygame.time.wait(1000) #pauses program for 1000ms for flash
            valve.drop()
            logging.info('Shape: {}'.format(objectT))

    print('Running in Raspberry PI = {}'.format(isRaspberryPI()))

    running = True
    off = False 

    # Main loop, run until the user asks to quit
    while running:
        #turn on/off visibility of mouse cursor (True=visible, False=hidden)
        #Turns visibility off if Raspberry pi is connected
        #if isRaspberryPI():
            #pygame.mouse.set_visible(off)
        
        #draw shape in middle of screen
        obj1= pygame.draw.circle(screen, yellow, (400,240), 100)
    
        # Draws invisible box in top right corner to return to menu
        closing_box = pygame.draw.rect(screen, black, (700,0, 100,100))

        mouse_pos = pygame.mouse.get_pos()
	
        eventsToCatch = [pygame.MOUSEBUTTONDOWN, pygame.FINGERUP]
        for event in pygame.event.get():
            #check for mousebutton 
            if event.type == pygame.MOUSEBUTTONDOWN or event.type==pygame.FINGERUP:
                print(event.type)
                mouse_pos= pygame.mouse.get_pos()
                print('The position of the cursor is', mouse_pos)
                logging.info('Coordinates:' + str(mouse_pos))
                left_click, pressed2, right_click = pygame.mouse.get_pressed() #pressed 1 is left click, pressed 3 is right click 
                if left_click or event.type==pygame.FINGERUP:
                    # Check if the object "collided" with the mouse pos and if the left mouse button was pressed
                    check_collision(obj1,mouse_pos)
                    # for obj in objList:
                    #     check_collision(obj,mouse_pos,left_click,white)

            #Check for events 
            if event.type == KEYDOWN: #escape from program
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    running = False
                # Pressing 'x' key stops behavioral test and returns to menu
                elif event.key == K_x:
                    return 
            elif event.type == pygame.QUIT:
                    running = False
            
            # When mouse is clicked or screen touched, a timer starts
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                timer = time.time()
            # When you unclick mouse or stop touching screen, timer stops

            # Records amount of  time you held mouse button or touched screen
            elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP:
                timer = time.time() - timer
                timer = str(timer)[:5]
                timer = float(timer)
                # Checks if screen was pressed in top right corner
                curs_in_box = closing_box.collidepoint(pygame.mouse.get_pos())
                # Returns to menu if top right corner was pressed for more than 2 seconds
                if curs_in_box and timer > 2:
                    print('User has pressed top right corner for 2 seconds. Returning to menu.')
                    running = False
                    #return      
    
        # Fill the background with black
        screen.fill(black)
        # Draw circles
        pygame.draw.circle(screen, yellow, (400,240), 100)
        # Draw invisible closing box
        pygame.draw.rect(screen, black, (700,0, 100,100))

        #if isRaspberryPI():
        #    pygame.mouse.set_pos(0,0)
            
        #Reset mouse position every loop to avoid problems with touchscreens. Comment this if using a computer
        #pygame.mouse.set_pos(0,0)

        # Update  the display
        pygame.display.flip()

    # Done! Time to quit.
    return

if __name__ == '__main__':
    pygame.init()
    behavioral_test_1()
    #pygame.quit()

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
