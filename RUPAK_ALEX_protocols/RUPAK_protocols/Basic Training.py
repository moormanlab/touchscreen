from touchscreen_protocol import BaseProtocol, Protocol, POINTERPRESSED, POINTERMOTION, POINTERRELEASED, tsColors, tTone
t1 = tTone(frequency = 1000, duration = 0.2, amplitude = 0.07)

dark_gray = tsColors['darkgray']
red = tsColors['red']

class Simple_Shape(Protocol):
    '''
    This example test protocol, based in the class 'Protocol' has the same functionality
    as test_1, but using the advantages of the Protocol class.
    The main difference is that the main function must not use a while loop.
    Instead it should include only the code for one single loop cycle and it will
    be continuously called from the protocol manager.
    '''
    def init(self):
        #self.log('This message will get lost in old log file')
        self.liqrew.set_drop_amount(2)
        self.pressed = False
        self.lastposition = 0
        self.set_log_filename('Simple Shape')
        self.log('Start training Simple Shape with new log file')
        self.Reward = False
        self.Running = True

    def main(self,event):
        if self.Running:
            rect1=self.draw.rect(color=red, start=(500,200), size=(100,100))
            self.screen.update()
            if event.type:
                if rect1.collidepoint(event.position):
                    self.sound.play(t1)
                    self.log('Sound played {}'.format(t1))
                    self.Reward = True
                    self.Running = False
        else:
            self.screen.clean()
            self.screen.update()


    def sensor_handler_in(self):
        self.log('subject at the spout')
        if (self.Reward):
            self.Reward = False
            self.liqrew.drop()
            self.sound.play(frequency=440, duration=.2, amplitude = .05)
            self.log('reward was given')

    def set_handler_out(self):
        self.log('subject left the spout')

    def end(self):
        self.log('End training Simple Shape')


class Advance_Shape(Protocol):
    '''
    This example test protocol, based in the class 'Protocol' has the same functionality
    as test_1, but using the advantages of the Protocol class.
    The main difference is that the main function must not use a while loop.
    Instead it should include only the code for one single loop cycle and it will
    be continuously called from the protocol manager.
    '''
    def init(self):
        #self.log('This message will get lost in old log file')
        self.liqrew.set_drop_amount(2)
        self.pressed = False
        self.lastposition = 0
        self.set_log_filename('Simple Shape')
        self.log('Start training Simple Shape with new log file')
        self.Reward = False
        self.Running = 1

    def main(self,event):
        if self.Running == 1:
            triangle1 = self.draw.polygon(tsColors['green'], 3, center = (250,270), radius = 63)
            circle1 = self.draw.circle(color=red, center=(500, 270), radius=57)
            self.screen.update()
            if event.type:
                if circle1.collidepoint(event.position):
                    self.Running = 2
        elif self.Running == 2:
            self.screen.clean()
            triangle1 = self.draw.polygon(tsColors['green'], 3, center=(500, 270), radius=63)
            circle1 = self.draw.circle(color=red, center=(250, 270), radius=57)
            self.screen.update()
            if event.type:
                if circle1.collidepoint(event.position):
                    self.sound.play(t1)
                    self.log('Sound played {}'.format(t1))
                    self.Reward = True
                    self.Running = 0
        else:
            self.screen.clean()
            self.screen.update()


    def sensor_handler_in(self):
        self.log('subject at the spout')
        if (self.Reward):
            self.Reward = False
            self.liqrew.drop()
            self.sound.play(frequency=440, duration=.2, amplitude = .05)
            self.log('reward was given')

    def set_handler_out(self):
        self.log('subject left the spout')

    def end(self):
        self.log('End training Simple Shape')


class Reward_Test(Protocol):
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


class Touch_Test(Protocol):
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
