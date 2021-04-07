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
from return_to_menu import return_to_menu
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
 

#Functions to add
''' 
- Add shapes (one function for each shape most likely, i.e circle, square, polygon)
- Check collison - Done
- Update screen?
-Play sound 
'''

# Puts entire script into function to call in menu script
def behavioral_test_1(screen):
    logger = logging.getLogger('BehTest1')
    logger.info('Behavioral Test 1 Started')

    buzz = Buzzer()
    def sensorHandler():
        logger.info('Decide what to do when the IRbeam was broken')

    sensor = IRSensor(sensorHandler)
    valve = Valve()

    # Import pygame.locals for easier access to key coordinates
    from pygame.locals import (
        K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_x
    )
    logging.info('Program Started')

    def check_collision(objectT, mouse_pos, color=(0,0,0)):
        '''
        Function to check if mouse click collides with one of the objects. 
        Takes in object, mouse position (tuple of coordinates) and pressed (boolean, True if mouse was clicked)
        Default argument for color is black, but can be changed. 
        '''
        if objectT.collidepoint(mouse_pos):
            logging.info('Shape: {}'.format(objectT))
            screen.fill(color)
            pygame.display.flip()
            return True

        return False

    logger.info('Running in Raspberry PI = {}'.format(isRaspberryPI()))

    running = True

    # Main loop, run until the user asks to quit
    while running:
        
        # Fill the background with black
        screen.fill(black)
        #draw test shapes
        obj1= pygame.draw.circle(screen, yellow, (75,250), 57)
        obj2= pygame.draw.circle(screen, purple , (260, 250), 57)
        obj3 = pygame.draw.rect(screen, red, (400,200, 100,100))
        obj4 = pygame.draw.rect(screen, blue, (600,200, 125,100))
        objList = [obj1,obj2,obj3,obj4]
        
        # Update  the display
        pygame.display.flip()

        eventsToCatch = [pygame.MOUSEBUTTONDOWN, pygame.FINGERUP]
        for event in pygame.event.get():
            #check for mousebutton 
            if event.type == pygame.MOUSEBUTTONDOWN or event.type==pygame.FINGERUP:
                logger.debug('Event {}'.format(event.type))
                mouse_pos= pygame.mouse.get_pos()
                logger.info('Coordinates:' + str(mouse_pos))
                left_click, pressed2, right_click = pygame.mouse.get_pressed() #pressed 1 is left click, pressed 3 is right click 
                if left_click or event.type==pygame.FINGERUP:
                    # Check if the object "collided" with the mouse pos and if the left mouse button was pressed
                    if (check_collision(obj1,mouse_pos, yellow) or
                        check_collision(obj2,mouse_pos, purple) or
                        check_collision(obj3,mouse_pos, red) or
                        check_collision(obj4,mouse_pos, blue) ):
                        buzz.play()
                        pygame.time.wait(1000) #pauses program for 1000ms for flash
                        valve.drop()

            if event.type == KEYDOWN: #escape from program
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    return
            elif event.type == pygame.QUIT:
                    return
            
            running = return_to_menu(event,screen)

    # Done! Time to quit.
    logger.info('Training Ended')
    return

beamBroken = False
beamTimer = 0
def sensorHandler():
    global beamBroken
    global beamTimer
    logging.info('IRbeam was broken')
    beamBroken = True
    beamTimer = time.time()

def operantConditioning(screen):
    logger = logging.getLogger('OpCond')
    logger.info('Operant Conditioning Started')

    # Initialize Reward-Setup
    global beamBroken
    global beamTimer
    buzz = Buzzer()
    valve = Valve()
    valve.setOpenTime(.05) # open time of valve, adjust as needed
    sensor = IRSensor(sensorHandler)

    # Import pygame.locals for easier access to key coordinates
    from pygame.locals import (
        K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_x
    )

    def check_collision(objectT, mouse_pos,color=(0,0,0)):
        '''
        Function to check if mouse click collides with one of the objects. 
        Takes in object, mouse position (tuple of coordinates) and pressed (boolean, True if mouse was clicked)
        Default argument for color is black, but can be changed. 
        '''
        if objectT.collidepoint(mouse_pos):
            logger.info('Shape selected: {}'.format(objectT))
            screen.fill(color)
            pygame.display.flip()
            return True
        
        return False

    logger.info('Running in Raspberry PI = {}'.format(isRaspberryPI()))

    running = True
    rewardGiven = False
    mouseAtWell = False
    rewardCount = 0

    # Main loop, run until the user asks to quit
    while running:
        
        # Fill the background with black
        screen.fill(black)
        # Draw circles
        obj1=pygame.draw.circle(screen, yellow, (400,340), 100)

        # Update  the display
        pygame.display.flip()
    
        if beamBroken == True:
            beamBroken = False
            mouseAtWell = True
            if rewardGiven == True:
                # a reward was given, the mouse is collecting
                logger.info('Mouse got reward')
                rewardGiven = False
            else:
                # there is no reward but mouse is exploring
                logger.info('Mouse at well without reward')
    
        if sensor.isPressed() == False:
            if mouseAtWell == True:
                #mouse has left the well
                timeAtWell = time.time() - beamTimer
                logger.info('Time spent at well: {:.2f}'.format(timeAtWell))
                mouseAtWell = False


        eventsToCatch = [pygame.MOUSEBUTTONDOWN, pygame.FINGERUP]
        for event in pygame.event.get():
            #check for mousebutton 
            if event.type == pygame.MOUSEBUTTONDOWN or event.type==pygame.FINGERUP:
                logger.debug('Event {}'.format(event.type))
                mouse_pos= pygame.mouse.get_pos()
                logger.info('Coordinates:' + str(mouse_pos))
                left_click, pressed2, right_click = pygame.mouse.get_pressed() #pressed 1 is left click, pressed 3 is right click 
                if left_click or event.type==pygame.FINGERUP:
                    # Check if the object "collided" with the mouse pos and if the left mouse button was pressed
                    if check_collision(obj1,mouse_pos):
                        buzz.play()
                        logger.info('Sound played')
                        pygame.time.wait(1000) #pauses program for 1000ms for flash
                        valve.drop()
                        rewardCount = rewardCount + 1
                        logger.info('Reward given. Total = {:d}'.format(rewardCount))
                        rewardGiven = True

            #Check for events 
            if event.type == KEYDOWN: #escape from program
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    return
            elif event.type == pygame.QUIT:
                    return
            
            running = return_to_menu(event,screen)
     
    logger.info('Training Ended')
    # Done! Time to quit.
    return

def classicalConditioning(screen):
    logger = logging.getLogger('ClassCond')
    logger.info('Classical Conditioning Started')

    # Initialize Reward-Setup
    global beamBroken
    global beamTimer
    buzz = Buzzer()
    valve = Valve()
    valve.setOpenTime(.05) # open time of valve, adjust as needed
    sensor = IRSensor(sensorHandler)

    # Import pygame.locals for easier access to key coordinates
    from pygame.locals import (
        K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_x
    )

    logger.info('Running in Raspberry PI = {}'.format(isRaspberryPI()))

    running = True
    rewardGiven = False
    finishTrial = False
    sleepTime = 3
    timeAtWell = 0
    mouseAtWell = False
    rewardCount = 0
    # Main loop, run until the user asks to quit
    while running:

        #Stops program for X seconds after a trial is completed 
        if finishTrial == True:
            #Turns screen gray to make sure it's working 
            screen.fill(gray)
            pygame.display.flip()
            #Sleeps program for X seconds
            time.sleep(sleepTime)
            logger.info('Finished Trial. Waiting to start next trial')
            finishTrial = False

        #Delivers reward and plays sound every time beam is broken 
        if beamBroken == True:
            beamBroken = False
            mouseAtWell = True
            logger.info('Mouse has entered well')
            buzz.play()
            logger.info('Sound played')
            valve.drop()
            rewardCount = rewardCount + 1
            logger.info('Reward given. Total = {:d}'.format(rewardCount))
    
        if (mouseAtWell == True) and (sensor.isPressed() == False):
            logger.info('Mouse has left well')
            mouseAtWell = False
            finishTrial = True
            timeAtWell = time.time() - beamTimer
            logging.info('Time spent at well: {:.2f}'.format(timeAtWell))


        eventsToCatch = [pygame.MOUSEBUTTONDOWN, pygame.FINGERUP]
        for event in pygame.event.get():
            #check for mousebutton 
            if event.type == pygame.MOUSEBUTTONDOWN or event.type==pygame.FINGERUP:
                logger.debug('Event {}'.format(event.type))
                mouse_pos= pygame.mouse.get_pos()
                logger.info('Coordinates:' + str(mouse_pos))

            #Check for events 
            if event.type == KEYDOWN: #escape from program
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    return
            elif event.type == pygame.QUIT:
                    return
            
            # When mouse is clicked or screen touched, the current time is recorded
            running = return_to_menu(event,screen)
    
        screen.fill(black)
        pygame.display.flip()

    logger.info('Training Ended')
    # Done! Time to quit.
    return


if __name__ == '__main__':
    pygame.init()
    if isRaspberryPI():
        surface = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
    else:
        surface = pygame.display.set_mode((800,480))
    behavioral_test_1(surface)
