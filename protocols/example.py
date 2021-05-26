from touchscreen_protocol import BaseProtocol, Protocol, POINTERPRESSED, POINTERMOTION, POINTERRELEASED
import touchscreen_protocol as ts

red = (255,0,0)

class Test1(BaseProtocol):
    '''
    This example Test protocol, based in the class 'BaseProtocol'
    requires use of pygame library
    It should control the main loop and the surface at all time.

    In the example when the pointer collides with the box it will end the training
    '''

    def init(self):
        self.setLogFile('Example Test 1')

    def main(self):
        import pygame
        running = True
        self.surface.fill((0,0,0))
        obj1 = pygame.draw.rect(self.surface, color=red, rect=(500,200, 100,100))
        pygame.display.flip()
        while running:
            for event in pygame.event.get():
                position = 0
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]:
                    position = event.pos
                elif event.type in [pygame.FINGERDOWN, pygame.FINGERMOTION,pygame.FINGERUP]:
                    position = (int(event.x*800),int(event.y*480))
                if position:
                    if obj1.collidepoint(position):
                        running = False

class Test2(Protocol):
    '''
    This example test protocol, based in the class 'Protocol' has the same functionality
    than test_1, but using the advantages of the Protocol class.
    The main difference is that the main function must not use a while loop.
    Instead it should include only the code for one single loop cycle and it will
    be continusly called from the protocol manager.
    '''
    def init(self):
        #self.log('This message will get lost in old log file')
        self.setLogFile('Example test 2')
        self.log('Start training Test2 with new logging file')

    def main(self,event):
        rect1=self.draw.rect(color=red, start=(500,200), size=(100,100))
        self.screen.update()
        if event.type:
            if rect1.collidepoint(event.position):
                self.quit()

    def end(self):
        self.log('End training Test2')

white = (255,255,255)
class TestingTouch(Protocol):
    '''
        This training protocol will deliver reward anytime the mouse touches the screen.
        A small circle is drawn where there is an interaction with the screen.
        This protocol only ends using the built in quiting procedure: touch in the upper left corner and slide up the upper right corner.
    '''
    def init(self):
        self.sensor.setHandler(self.sensorHandler)
        self.valve.setOpenTime(.03)
        self.pressed = False
        self.lastposition = 0
        self.log('Test Started')

    def main(self,event):
        self.screen.clean()
        if self.pressed:
            self.draw.circle(white, self.lastposition, 20)
        self.screen.update()

        if event.type == POINTERPRESSED:
            self.pressed = True
            self.draw.circle(white, event.position, 20)
            self.lastposition = event.position
            self.screen.update()
            self.sound.play(frec=440,duration=.2)
            self.log('Valve drop, giving reward')
            self.valve.drop()
            self.log('pointer pressed at {:03d}, {:03d}'.format(event.position[0],event.position[1]))

        elif event.type == POINTERMOTION:
            self.lastposition = event.position
            self.log('pointer moving')

        elif event.type == POINTERRELEASED:
            self.pressed = False
            self.lastposition = 0
            self.log('pointer released at {:03d}, {:03d}'.format(event.position[0],event.position[1]))

    def sensorHandler(self):
        self.log('Decide what to do when the IRbeam was broken')

    def end(self):
        self.setNote()
        self.log('ended training')


#This Test will not be loaded because it is missing correct inheritance
class Test(object):

    def init(self):
        pass
