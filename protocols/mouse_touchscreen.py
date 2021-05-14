'''
Mouse Touchscreen Program, Moorman Lab 2020 
Code written by Jason Biundo, version 1.1 10/2020

This program utilizes the pygame library to create an interactive program that mice can 
interact with on a touchscreen that is run by a Raspberry pi. This program is designed to 
eventually be generalizable to a variety of different tasks.
'''
from touchscreen_protocol import BaseProtocol, Protocol, POINTERPRESSED, POINTERMOTION, POINTERRELEASED
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

import pygame
from pygame.locals import (
    K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_x
)
import logging
from hal import isRaspberryPI
from return_to_menu import return_to_menu
import time
# Puts entire script into function to call in menu script
class behavioral_test_base(BaseProtocol):

    def init(self):
        self.sensor.setHandler(self.sensorHandler)
    #buzz = Buzzer()
    def sensorHandler(self):
        logging.info('Decide what to do when the IRbeam was broken')

    #sensor = IRSensor(sensorHandler)
    #valve = Valve()

    # Import pygame.locals for easier access to key coordinates

    def check_collision(self, objectT, mouse_pos, color=(0,0,0)):
        '''
        Function to check if mouse click collides with one of the objects. 
        Takes in object, mouse position (tuple of coordinates) and pressed (boolean, True if mouse was clicked)
        Default argument for color is black, but can be changed. 
        '''
        if objectT.collidepoint(mouse_pos):
            logging.info('Shape: {}'.format(objectT))
            self.surface.fill(color)
            pygame.display.flip()
            return True

        return False


    def main(self):
        logger = logging.getLogger('BehTest1')
        logger.info('Behavioral Test 1 Started')
        logger.info('Running in Raspberry PI = {}'.format(isRaspberryPI()))
        running = True
        screen = self.surface
        # Main loop, run until the user asks to quit
        while running:
        
        # Fill the background with black
            screen.fill(black)
        #draw test shapes
            obj1 = pygame.draw.circle(screen, yellow, (75,250), 57)
            obj2 = pygame.draw.circle(screen, purple , (260, 250), 57)
            obj3 = pygame.draw.rect(screen, red, (400,200, 100,100))
            obj4 = pygame.draw.rect(screen, blue, (600,200, 125,100))
            objList = [obj1,obj2,obj3,obj4]
        
        # Update  the display
            pygame.display.flip()

            for event in pygame.event.get():
                #check for mousebutton 
                if event.type == pygame.MOUSEBUTTONDOWN or event.type==pygame.FINGERDOWN:
                    logger.debug('Event {}'.format(event.type))
                    mouse_pos= pygame.mouse.get_pos()
                    logger.info('Coordinates:' + str(mouse_pos))
                    left_click, pressed2, right_click = pygame.mouse.get_pressed() #pressed 1 is left click, pressed 3 is right click 
                    if left_click or event.type==pygame.FINGERDOWN:
                        # Check if the object "collided" with the mouse pos and if the left mouse button was pressed
                        if (self.check_collision(obj1,mouse_pos, yellow) or
                            self.check_collision(obj2,mouse_pos, purple) or
                            self.check_collision(obj3,mouse_pos, red) or
                            self.check_collision(obj4,mouse_pos, blue) ):
                            self.sound.play()
                            #pygame.time.wait(1000) #pauses program for 1000ms for flash
                            self.valve.drop()

                if event.type == KEYDOWN: #escape from program
                    # Was it the Escape key? If so, stop the loop.
                    if event.key == K_ESCAPE:
                        return
                elif event.type == pygame.QUIT:
                        return
            
                running = not return_to_menu(event)

        # Done! Time to quit.
        logger.info('Training Ended')
        return


class behavioral_test_protocol(Protocol):
    def init(self):
        self.setLoggerName('BehTest1')
        from hal import isRaspberryPI
        self.log('Running in Raspberry PI = {}'.format(isRaspberryPI()))
        self.log('Behavioral Test 1 Started')

    def sensorHandler(self):
        self.log('Decide what to do when the IRbeam was broken')


    def check_collision(self, objectT, mouse_pos, color=(0,0,0)):
        '''
        Function to check if mouse click collides with one of the objects. 
        Takes in object, mouse position (tuple of coordinates) and pressed (boolean, True if mouse was clicked)
        Default argument for color is black, but can be changed. 
        '''
        if objectT.collidepoint(mouse_pos):
            self.log('Shape: {}'.format(objectT))
            self.screen.fill(color)
            self.screen.update()
            return True

        return False

    def main(self,event):
        
        # Fill the background with black
        self.screen.clean()
        #draw test shapes
        obj1= self.draw.circle(yellow, (75,250), 57)
        obj2= self.draw.polygon(purple, 5, (260, 250), 57)
        #obj3 = self.draw.rect(red, start=(400,200), size=(100,100))
        obj3 = self.draw.polygon(red, 3, center=(450,270), radius=63)
        obj4 = self.draw.rect(blue, start=(600,200), size=(125,100))
        objList = [obj1,obj2,obj3,obj4]
        
        # Update  the display
        self.screen.update()

        if event.type == POINTERPRESSED:
            self.log(event)
            mouse_pos= event.position
            self.log('Coordinates:' + str(mouse_pos))
            # Check if the object "collided" with the mouse pos and if the left mouse button was pressed
            if (self.check_collision(obj1,mouse_pos, yellow) or
                self.check_collision(obj2,mouse_pos, purple) or
                self.check_collision(obj3,mouse_pos, red) or
                self.check_collision(obj4,mouse_pos, blue) ):
                self.sound.play()
                #self.pause(1)
                self.valve.drop()

        return
#
    def end(self):
        self.log('Finished')
#
#
#
#
import time
class operantConditioning(Protocol):

    def init(self):
        self.setLoggerName('OpCond')
        self.log('Operant Conditioning Started')
        self.valve.setOpenTime(.02) # open time of valve, adjust as needed
        self.beamBroken = False
        self.beamTimer = 0
        #self.running = True
        self.rewardGiven = False
        self.mouseAtWell = False
        self.rewardCount = 0
        self.screen.setBackcolor = (0,0,0)

    def sensorHandler(self):
        self.log('IRbeam was broken')
        self.beamBroken = True
        self.beamTimer = time.time()

    def check_collision(self,objectT, mouse_pos,color=(0,0,0)):
        '''
        Function to check if mouse click collides with one of the objects. 
        Takes in object, mouse position (tuple of coordinates) and pressed (boolean, True if mouse was clicked)
        Default argument for color is black, but can be changed. 
        '''
        if objectT.collidepoint(mouse_pos):
            self.log('Shape selected: {}'.format(objectT))
            self.screen.fill(color)
            self.screen.update()
            return True
        
        return False

    def main(self,event):
        # Fill the background with black
        self.screen.clean()
        # Draw circles
        obj1=self.draw.rect(black, start=(0,0), size=(800,480))

        # Update  the display
        self.screen.update()
    
        if self.beamBroken == True:
            self.beamBroken = False
            self.mouseAtWell = True
            if self.rewardGiven == True:
                # a reward was given, the mouse is collecting
                self.log('Mouse got reward')
                self.rewardGiven = False
            else:
                # there is no reward but mouse is exploring
                self.log('Mouse at well without reward')
    
        if self.sensor.isPressed() == False:
            if self.mouseAtWell == True:
                #mouse has left the well
                self.timeAtWell = time.time() - self.beamTimer
                self.log('Time spent at well: {:.2f}'.format(self.timeAtWell))
                self.mouseAtWell = False

        sleepTime = 3

        if event.type == POINTERPRESSED:
            mouse_pos = event.position
            self.log('Coordinates:' + str(mouse_pos))
            # Check if the object "collided" with the mouse pos and if the left mouse button was pressed
            if self.check_collision(obj1,mouse_pos):
                self.sound.play()
                self.log('Sound played')
                self.screen.fill(gray)
                self.screen.update()
                self.valve.drop()
                self.rewardCount = self.rewardCount + 1
                self.log('Reward given. Total = {:d}'.format(self.rewardCount))
                self.rewardGiven = True
                time.sleep(sleepTime)

    def end(self):   
        self.log('Training Ended')
        self.log('Results {}'.format(self.rewardCount))



class classicalConditioning(Protocol):
    def init(self):
        self.setLoggerName('ClassCond')
        self.log('Classical Conditioning Started')
        self.valve.setOpenTime(.05) # open time of valve, adjust as needed
        self.rewardGiven = False
        self.finishTrial = False
        self.sleepTime = 3
        self.timeAtWell = 0
        self.mouseAtWell = False
        self.rewardCount = 0
        self.beamBroken = False
        self.beamTimer = 0


    def sensorHandler(self):
        self.log('IRbeam was broken')
        self.beamBroken = True
        self.beamTimer = time.time()


    def main(self,event):
        self.screen.fill(black)
        self.screen.update()
        #Stops program for X seconds after a trial is completed 
        if self.finishTrial == True:
            #Turns screen gray to make sure it's working 
            self.screen.fill(gray)
            self.screen.update()
            #Sleeps program for X seconds
            time.sleep(self.sleepTime)
            self.log('Finished Trial. Waiting to start next trial')
            self.finishTrial = False

        #Delivers reward and plays sound every time beam is broken 
        if self.beamBroken == True:
            self.beamBroken = False
            self.mouseAtWell = True
            self.log('Mouse has entered well')
            self.sound.play()
            self.log('Sound played')
            self.valve.drop()
            self.rewardCount += 1
            self.log('Reward given. Total = {:d}'.format(self.rewardCount))
    
        if (self.mouseAtWell == True) and (self.sensor.isPressed() == False):
            self.log('Mouse has left well')
            self.mouseAtWell = False
            self.finishTrial = True
            self.timeAtWell = time.time() - self.beamTimer
            self.log('Time spent at well: {:.2f}'.format(self.timeAtWell))

        if event.type == POINTERPRESSED:
            self.log('Event {}'.format(event.type))
            mouse_pos= pygame.mouse.get_pos()
            self.log('Coordinates:' + str(mouse_pos))

    def end(self):
        self.log('Training Ended')
        self.log('Results {}'.format(self.rewardCount))
#
#if __name__ == '__main__':
#    pygame.init()
#    if isRaspberryPI():
#        surface = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
#        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
#    else:
#        surface = pygame.display.set_mode((800,480))
#    behavioral_test_1(surface)
