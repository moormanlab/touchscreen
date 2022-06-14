'''
Mouse Touchscreen Program, Moorman Lab 2020 
Code written by Jason Biundo, version 1.1 10/2020
Updated by Ariel Burman, 04/2021

'''
from touchscreen_protocol import BaseProtocol, Protocol, POINTERPRESSED, POINTERMOTION, POINTERRELEASED
#colors
from csv_logging import CSVLogger
from touchscreen_protocol import tTone
t1 = tTone(frequency = 2000, duration = 0.2, amplitude = 0.3)

from touchscreen_protocol import tsColors
red    = tsColors['red']
green  = tsColors['green']
blue   = tsColors['blue']
black  = tsColors['black']
yellow = tsColors['yellow']
dark_gray = tsColors['darkgray']
deepskyblue = tsColors['deepskyblue']
REWARD_WINDOW = 15.0
INTER_TOUCHS_TIME = 1.0

class OperantConditioning(Protocol):
    '''
    In this training the animal has to touch the screen to get a reward.
    A Reward is delivered if the animal goes to the spout within the reward window time.
    '''

    def init(self):
        self.set_log_filename('OpCond')
        self.csvlogger.configure(header=['reward_count', 'rewards_missed', 'no_reward'], replace=False)
        self.csvlogger.start()
        drops = 50
        self.liqrew.set_drop_amount(drops) # drop amount, adjust as needed
        self.log(self.csvlogger.log(event=f'Operant Conditioning Started, reward set to {drops} drop(s)'))
        self.beam_broken = False
        self.beam_timer = 0
        self.mouse_at_spout = False
        self.touch_time = 0
        self.reward_count = 0
        self.reward_missed = 0
        self.no_reward = 0
        self.reward_active = False
        #self.screen.setBackcolor((0,0,0))
        #self.set_note('Weight')

    def sensor_handler_in(self):
        self.log('IRbeam was broken')
        self.csvlogger.log(event='IRbeam broken')
        self.beam_broken = True
        self.beam_timer = self.now()
    def sensor_handler_out(self):
        self.csvlogger.log(event='IRbeam released')

    def main(self,event):
        # Fill the background with black
        self.screen.clean()

        if self.reward_active == True:
            if self.now() - self.touch_time > REWARD_WINDOW:
                self.reward_active = False
                self.log('Animal did not come for reward')
                self.reward_missed += 1
                self.log('Reward missed. Total = {:d}'.format(self.reward_missed))
                self.csvlogger.log(event='Reward missed', rewards_missed=self.reward_missed)
            else:
                self.screen.fill((0,85,85))
        
        self.screen.update()

        if self.beam_broken == True:
            self.mouse_at_spout = True
            if self.reward_active == True:
                self.liqrew.drop()
                # a reward was given, the mouse is collecting
                self.reward_count += 1
                self.log('Animal got reward. Total = {:d}'.format(self.reward_count))
                self.csvlogger.log(event='Reward recieved', reward_count=self.reward_count)
                self.reward_active = False
            else:
                # there is no reward but mouse is exploring
                self.log('Mouse at well without reward')
                self.no_reward += 1
                self.csvlogger.log(event='No reward active', no_reward=self.no_reward)
            self.beam_broken = False
    
        if self.sensor.is_activated() == False:
            if self.mouse_at_spout == True:
                #mouse has left the well
                self.time_at_spout = self.now() - self.beam_timer
                self.log('Time spent at spout: {:.2f}'.format(self.time_at_spout))
                self.mouse_at_spout = False

        if event.type == POINTERPRESSED:
            if self.now() - self.touch_time > INTER_TOUCHS_TIME:
                self.touch_time = self.now()
                mouse_pos = event.position
                self.log('Coordinates:' + str(mouse_pos))
                if self.reward_active == True:
                    self.log('Animal did not come for last reward')
                self.sound.play(t1)
                self.log('Sound played {}'.format(t1))
                self.reward_active = True

    def end(self):   
        self.log('Training Ended')
        self.log('Total rewards {}'.format(self.reward_count))
        self.log('Total missed {}'.format(self.reward_missed))
        self.csvlogger.log(event='Training ended', reward_count=self.reward_count, rewards_missed=self.reward_missed, no_reward=self.no_reward)



class ClassicalConditioning(Protocol):
    '''
        Whenever the mouse goes to the spout there is a sound played and 
        immediately after there will be a reward. There is a window of no
        reward after the mouse leaves the spout
    '''

    def init(self):
        self.csvlogger.configure(header=['reward_count'], replace=False)
        self.csvlogger.start()
        self.set_log_filename('ClassCond')
        self.log('Classical Conditioning Started')
        drops = 50
        self.liqrew.set_drop_amount(drops) # drop amount of liquid reward, adjust as needed
        self.csvlogger.log(event=f'Classical Conditioning Started, reward set to {drops} drop(s)')
        self.rewardGiven = False
        self.finishTrial = False
        self.sleepTime = 5
        self.timeAtWell = 0
        self.mouseAtWell = False
        self.rewardCount = 0
        self.beamBroken = False
        self.beamTimer = 0


    def sensor_handler_in(self):
        self.log('IRbeam was broken')
        self.csvlogger.log(event='mouse entered well')
        self.beamBroken = True
        self.beamTimer = self.now()

    def sensor_handler_out(self):
        self.log('IRbeam was released')
        self.csvlogger.log(event='mouse left well')

    def main(self,event):
        self.screen.fill(black)
        self.screen.update()

        #Stops program for X seconds after a trial is completed 
        if self.finishTrial == True:
            #Turns screen gray to make sure it's working 
            self.screen.fill((0, 85, 85))
            self.screen.update()
            #Sleeps program for X seconds
            self.pause(self.sleepTime)
            self.log('Finished Trial. Waiting to start next trial')
            self.finishTrial = False
            self.beamBroken = False
            self.rewardGiven = False

        #Delivers reward and plays sound every time beam is broken 
        if self.beamBroken == True:
            self.mouseAtWell = True
            self.log('Mouse has entered well')
            if not self.rewardGiven:
                self.sound.play(t1)
                self.log('Sound played {}'.format(t1))
                self.csvlogger.log(event=f'sound played: {t1}')
                self.liqrew.drop()
                self.rewardCount += 1
                self.csvlogger.log(reward_count=self.rewardCount, event='reward given')
                self.rewardGiven = True
                self.log('Reward given. Total = {:d}'.format(self.rewardCount))
            else:
                self.log('Reward for this trial already delivered')
    
        if (self.mouseAtWell == True) and (self.sensor.is_activated() == False):
            self.log('Mouse has left well')
            self.mouseAtWell = False
            self.finishTrial = True
            self.timeAtWell = self.now() - self.beamTimer
            self.log('Time spent at well: {:.2f}'.format(self.timeAtWell))

        if event.type == POINTERPRESSED:
            self.log('Event {}'.format(event.type))
            mouse_pos= pygame.mouse.get_pos()
            self.log('Coordinates:' + str(mouse_pos))

    def end(self):
        self.log('Training Ended')
        self.log('Results {}'.format(self.rewardCount))



class BehavioralTestProtocol(Protocol):
    '''
    This program is similar to the behavioral test using the advantages provided by
    the Protocol class.

    There are three important parts of the program. 'init', 'main' and end.
    Only main is mandatory.

    The sensor_handler is called whenever the mouse is reaches the spout

    '''
    def init(self):
        self.set_log_filename('BehTest1')
        self.log('Behavioral Test 1 Started')

    def sensor_handler_in(self):
        self.log('Decide what to do when the IRbeam was broken')

    def check_collision(self, objectT, mouse_pos):
        '''
        Function to check if mouse click collides with one of the objects. 
        Takes in object, mouse position (tuple of coordinates)
        Using object color to fill the screen 
        '''
        if objectT.collidepoint(mouse_pos):
            self.log('Shape: {}'.format(objectT))
            self.screen.fill(objectT.color)
            self.screen.update()
            return True

        return False

    def main(self,event):
        '''
        The main function will be called "fps" times per second.
        
        Although it is not mandatory, it should not have any long pause.
        '''
        
        # Fill the background with black
        self.screen.clean()
        #draw test shapes
        obj1 = self.draw.circle(color = yellow, center = (75,250), radius = 57)
        obj2 = self.draw.polygon(color = tsColors['green'], n_sides = 5, center = (260, 250), radius = 57)
        obj3 = self.draw.polygon(tsColors['red'], 3, center = (450,270), radius = 63)
        obj4 = self.draw.rect('blue', start = (600,200), size = (125,100))
        
        # Update  the display
        self.screen.update()

        if event.type == POINTERPRESSED:
            self.log(event)
            mouse_pos = event.position
            self.log('Coordinates:' + str(mouse_pos))
            # Check if the object "collided" with the mouse pos and if the left mouse button was pressed
            if (self.check_collision(obj1, mouse_pos) or
                self.check_collision(obj2, mouse_pos) or
                self.check_collision(obj3, mouse_pos) or
                self.check_collision(obj4, mouse_pos) ):
                self.sound.play(frequency=1000, duration = .2)
                self.liqrew.drop()

        return

    def end(self):
        #self.set_note('Something the user would like to write in the log file')
        self.log('Finished')



'''
The following imports are needed only for BehavioralTestBase
and usually are not required when using the Protocol class.
'''

import pygame
from pygame.locals import (
    K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_x
)
import logging
from return_to_menu import return_to_menu
import time

red    = ( 255,   0,   0)
green  = (   0, 255,   0)
blue   = (   0,   0, 255)
black  = (   0,   0,   0)
yellow = ( 255, 255,   0)
white  = ( 255, 255, 255)

class BehavioralTestBase(BaseProtocol):
    '''
    This program utilizes the pygame library to create an interactive program that mice can 
    interact with on a touchscreen that is run by a Raspberry pi. This program is designed to 
    eventually be generalizable to a variety of different tasks.
    This example gets control of the main loop and it should be used when there is need to 
    use any feature not contemplated in the Protocol Class.
    '''
    def init(self):
        self.sensor.set_handler_in(self.sensor_handler)

    def sensor_handler(self):
        logging.info('Decide what to do when the IRbeam was broken')

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
        running = True
        screen = self.surface
        # Main loop, run until the user asks to quit
        while running:
        
            # Fill the background with black
            screen.fill(black)
            #draw test shapes
            obj1 = pygame.draw.circle(screen, yellow, (75,250), 57)
            obj2 = pygame.draw.circle(screen, green, (260, 250), 57)
            obj3 = pygame.draw.rect(screen, red, (400,200, 100,100))
            obj4 = pygame.draw.rect(screen, blue, (600,200, 125,100))
        
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
                            self.check_collision(obj2,mouse_pos, green) or
                            self.check_collision(obj3,mouse_pos, red) or
                            self.check_collision(obj4,mouse_pos, blue) ):
                            self.sound.play()
                            #pygame.time.wait(1000) #pauses program for 1000ms for flash
                            self.liqrew.drop()

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


if __name__ == '__main__':
    pygame.init()
    from Touchscreen_menu import create_surface, protocol_run
    surface = create_surface()
    protocol_run(BehavioralTestBase,surface,['Ariel','pepe'])
