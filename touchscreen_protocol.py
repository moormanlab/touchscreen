import logging
import pygame
from abc import ABC, abstractmethod

from hal import isRaspberryPI, LiqReward, IRSensor, Sound
from keyboard import keyboard
from utils import POINTERPRESSED, POINTERMOTION, POINTERRELEASED, getPosition, tsColors
from return_to_menu import return_to_menu
import shapes
from sound import tTone

logger = logging.getLogger('TouchProtocols')


class tsEvent(object):
    def __init__(self,typeEv=None,posEv=(-1,-1)):
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


class BaseProtocol(ABC):

    def __init__(self, surface, subject=None, experimenter=None):
        self._type = 'BaseProtocol'
        self.surface = surface
        self.liqrew = LiqReward()
        self.sensor = IRSensor(self.sensor_handler)
        self.sound = Sound()
        logger.debug('Sensor variant {}'.format(self.sensor.get_type()))
        logger.debug('Sound variant {}'.format(self.sound.get_type()))
        logger.debug('Liquid reward variant {}'.format(self.liqrew.get_type()))
        self._logfile = None
        self.subject = subject
        self.experimenter = experimenter
        self.logger = logging.getLogger('Protocol')
    
    def _init(self,logHdlr):
        self._logHdlr = logHdlr
        self._logfile = self._logHdlr.baseFilename
        self.logger = logging.getLogger(self.__class__.__name__)
        logger.info('Setting log file to {}'.format(self._logfile))
        self.logger.addHandler(self._logHdlr)
        logger.debug('Protocol type {}'.format(self._type))
        self.init()

    def _run(self):
        logger.info('Start running baseprotocol {}'.format(self.__class__.__name__))
        self.main()

    def _end(self):
        logger.info('End running baseprotocol {}'.format(self.__class__.__name__))
        self.end()
    
    def set_log_filename(self, filename):
        import datetime, os
        oldlogfile = self._logHdlr.baseFilename
        logPath = os.path.dirname(oldlogfile)
        self._logHdlr.close()

        #preparing log filename
        now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
        filename = filename + '_' + now + '.log'
        filename = filename.replace(' ','_')

        self._logHdlr.baseFilename = os.path.join(logPath, filename)
        self._logfile = self._logHdlr.baseFilename
        logger.info('Changing log file to {}'.format(self._logfile))
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.addHandler(self._logHdlr)
        #delete old file
        if os.path.isfile(oldlogfile):
            logger.debug('Removing old log file to {}'.format(oldlogfile))
            os.remove(oldlogfile)

    def log(self,string):
        self.logger.info(string)

    def sensor_handler(self):
        pass

    def init(self):
        pass

    def main(self):
        raise NotImplementedError

    def end(self):
        pass


class Protocol(BaseProtocol):

    class Screen(object):
        def __init__(self,surface,backcolor=(0,0,0)):
            self.surface = surface
            self.backcolor = backcolor
            self.width, self.height = surface.get_size()

        def setBackcolor(self,color):
            self.backcolor = color

        def update(self):
            return pygame.display.flip()

        def fill(self,color):
            return self.surface.fill(color)

        def clean(self):
            return self.surface.fill(self.backcolor)

        def get_size(self):
            return self.width, self.height

        def get_height(self):
            return self.height

        def get_width(self):
            return self.width


    def __init__(self, surface, subject=None, experimenter=None, backcolor=tsColors['black']):
        super().__init__(surface, subject, experimenter)
        self.screen = Protocol.Screen(surface,backcolor)
        self.draw = shapes.Draw(surface)
        self._archpi = isRaspberryPI()
        self._type = 'Protocol'
        self._exit = False
        self._fps = 60

    def _run(self):
        self.screen.clean()
        self.screen.update()
        logger.info('Start running protocol {}'.format(self.__class__.__name__))
        pressed = False
        clock = pygame.time.Clock()
        while not self._exit:
            clock.tick(self._fps)
            events = pygame.event.get()
            if events:
              for event in events:
                logger.debug(event)
                tEvent = tsEvent()
                tEvent.position = getPosition(event)

                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                    tEvent.type = POINTERPRESSED
                    pressed = True
                elif event.type in [pygame.MOUSEMOTION, pygame.FINGERMOTION] and pressed:
                    tEvent.type = POINTERMOTION
                elif event.type in [pygame.MOUSEBUTTONUP, pygame.FINGERUP]:
                    tEvent.type = POINTERRELEASED
                    pressed = False

                if tEvent.type:
                    self.logger.debug('{}: Coord ({},{})'.format(str(tEvent.get_type()),tEvent.position[0],tEvent.position[1]))

                # only on PC
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or event.type == pygame.QUIT:
                    return

                if return_to_menu(event):
                    return

                self.main(tEvent)
            else:
                self.main(tsEvent())


    def _end(self):
        logger.info('End running protocol {}'.format(self.__class__.__name__))
        self.end()

    def main(self,event):
        pass

    def pause(self,sleeptime):
        import time
        time.sleep(sleeptime)

    def quit(self):
        self._exit = True

    def setMaxFPS(self, fps: int):
        #assert isinstance(fps, int)
        self._fps = fps

    def setNote(self,title=None):
        note = keyboard(self.surface)
        if note != '':
            if title == None:
                title = 'Note'
            self.log('{}: {}'.format(title,note))
