from hal import isRaspberryPI, Valve, IRSensor, Buzzer
import logging
import pygame

logger = logging.getLogger('TouchProtocols')

POINTERPRESSED = 1
POINTERMOTION = 2
POINTERRELEASED = 3

tsColors = {
        'red': (255,0,0),
        'green': (0,255,0),
        'blue': (0,0,255),
        'black': (0,0,0),
        'yellow': (255,255,0),
        'purple': (255,0,255),
        'white': (255,255,255),
        'deepskyblue': (0,191,255),
        'gray': (128,128,128),
        'darkgray': (64, 64, 64),
        }

class tsEvent(object):
    def __init__(self,typeEv=None,posEv=(0,0)):
        self.type = typeEv
        self.position = posEv

    def __str__(self):
        string = 'tsEvent: {}, Coord: {}'.format(self.get_type(),self.position)
        return string

    def get_type(self):
        if self.type == POINTERPRESSED:
            return 'PointerPressed'
        elif self.type == POINTERMOTION:
            return 'PointerMotion'
        elif self.type == POINTERRELEASED:
            return 'PointerReleased'
        else:
            return 'None'


from pygame.locals import (
    K_ESCAPE, KEYDOWN
    )
from return_to_menu import return_to_menu
import shapes


class BaseProtocol(object):

    def __init__(self,surface):
        self._type = 'BaseProtocol'
        self.surface = surface
        self.valve = Valve()
        self.sensor = IRSensor(self.sensorHandler)
        self.sound = Buzzer()
    
    def _init(self):
        logger.debug('Protocol type {}'.format(self._type))
        self.init()

    def _run(self):
        logger.debug('Start running baseprotocol')
        self.main()

    def _end(self):
        logger.debug('End running baseprotocol')
        self.end()
    
    def sensorHandler(self):
        pass

    def init(self):
        pass

    def main(self):
        pass

    def end(self):
        pass


class Protocol(BaseProtocol):

    class Screen(object):
        def __init__(self,surface,backcolor=(0,0,0)):
            self.surface = surface
            self.backcolor = backcolor

        def setBackcolor(self,color):
            self.backcolor = color

        def update(self):
            return pygame.display.flip()

        def fill(self,color):
            return self.surface.fill(color)

        def clean(self):
            return self.surface.fill(self.backcolor)


    def __init__(self,surface,backcolor=(0,0,0)):
        BaseProtocol.__init__(self,surface)
        self.screen = Protocol.Screen(surface)
        self.draw = shapes.Draw(surface)
        self.backcolor = backcolor
        self._type = 'Protocol'
        self.logger = logging.getLogger('Protocol')

    def setLoggerName(self,name):
        self.logger = logging.getLogger(name)

    def log(self,string):
        self.logger.info(string)

    def _run(self):
        self.surface.fill((0,0,0))
        pygame.display.flip()
        self.logger.debug('Start running protocol')
        running = True
        while running:
            events = pygame.event.get()
            if events:
              for event in events:
                tEvent = tsEvent()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    tEvent.type = POINTERPRESSED
                    tEvent.position = event.pos
                elif event.type == pygame.FINGERDOWN:
                    tEvent.type = POINTERPRESSED
                    tEvent.position = (int(event.x*800),int(event.y*480))
                elif event.type == pygame.MOUSEMOTION:
                    tEvent.type = POINTERMOTION
                    tEvent.position = event.pos
                elif event.type == pygame.FINGERMOTION:
                    tEvent.type = POINTERMOTION
                    tEvent.position = (int(event.x*800),int(event.y*480))
                elif event.type == pygame.MOUSEBUTTONUP:
                    tEvent.type = POINTERRELEASED
                    tEvent.position = event.pos
                elif event.type == pygame.FINGERUP:
                    tEvent.type = POINTERRELEASED
                    tEvent.position = (int(event.x*800),int(event.y*480))

                if tEvent.type:
                    self.logger.debug('{}: Coord ({},{})'.format(str(tEvent.get_type()),tEvent.position[0],tEvent.position[1]))

                # only on PC
                if event.type == KEYDOWN: #escape from program
                    # Was it the Escape key? If so, stop the loop.
                    if event.key == K_ESCAPE:
                        return
                elif event.type == pygame.QUIT:
                    return

                if return_to_menu(event,self.surface):
                    return

                self.main(tEvent)
            else:
                self.main(tsEvent())

    def _end(self):
        self.logger.debug('End running protocol')
        self.end()

    def main(self,event):
        pass

    def pause(self,sleeptime):
        import time
        time.sleep(sleeptime)
