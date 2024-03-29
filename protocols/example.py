from touchscreen_protocol import BaseProtocol, Protocol, POINTERPRESSED, POINTERMOTION, POINTERRELEASED, tsColors

dark_gray = tsColors['darkgray']
red = tsColors['red']

class Test1(BaseProtocol):
    '''
    This example test protocol, based in the class 'BaseProtocol'
    requires use of pygame library
    It should control the main loop and the surface at all time.

    In the example when the pointer collides with the box it will end the training
    There are three method for the control sequence: 'init', 'main' and 'end'.
    Only 'main' is mandatory
    '''

    def init(self):
        self.set_log_filename('Example Test 1')

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
    be continuously called from the protocol manager.
    '''
    def init(self):
        #self.log('This message will get lost in old log file')
        self.set_log_filename('Example test 2')
        self.log('Start training Test2 with new logging file')

    def main(self,event):
        rect1=self.draw.rect(color=red, start=(500,200), size=(100,100))
        self.screen.update()
        if event.type:
            if rect1.collidepoint(event.position):
                self.quit()

    def end(self):
        self.log('End training Test2')



class TestingReward(Protocol):
    '''
        This training protocol, base on the 'Protocol' class will deliver
        reward anytime the mouse reachs the spout.
        This protocol uses the default handlers name, so there is no need to set
        the handlers (they are already setted).
        This protocol only ends using the built-in quitting procedure: touch in
        the upper left corner and slide up to the upper right corner.
    '''
    def init(self):
        self.liqrew.set_drop_amount(2)
        self.pressed = False
        self.lastposition = 0
        self.log('Test Started')

    def sensor_handler_in(self):
        self.log('subject at the spout')
        self.liqrew.drop()
        self.sound.play(frequency=440, duration=.2, amplitude = .05)

    def set_handler_out(self):
        self.log('subject left the spout')

    def end(self):
        self.set_note()
        self.log('Ended training')


white = tsColors['white']

class TestingTouch(Protocol):
    '''
        This training protocol, base on the 'Protocol' class will deliver
        reward anytime the mouse touches the screen.  A small circle is drawn
        where there is an interaction with the screen.  This protocol only ends
        using the built-in quitting procedure: touch in the upper left corner
        and slide up to the upper right corner.
    '''
    def init(self):
        self.sensor.set_handler_in(self.break_in)
        self.sensor.set_handler_out(self.break_out)
        self.liqrew.set_drop_amount(5)
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
            self.sound.play(frequency=440, duration=.2, amplitude = .05)
            self.log('Valve drop, giving reward')
            self.liqrew.drop()
            self.log('Pointer pressed at {:03d}, {:03d}'.format(event.position[0],event.position[1]))


        elif event.type == POINTERMOTION:
            self.lastposition = event.position
            self.log('Pointer moving')

        elif event.type == POINTERRELEASED:
            self.pressed = False
            self.lastposition = 0
            self.log('Pointer released at {:03d}, {:03d}'.format(event.position[0],event.position[1]))

    def break_in(self):
        self.log('subject at the spout')

    def break_out(self):
        self.log('subject left the spout')

    def end(self):
        self.set_note()
        self.log('Ended training')


class Test(object):
    '''
       This Test will not be loaded because it is missing correct inheritance.
       Either 'Protocol' or 'BaseProtocol'
    '''
    def init(self):
        pass
