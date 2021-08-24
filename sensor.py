import time
import logging
from gpiozero import DigitalInputDevice
from gpiozero.pins.mock import MockFactory
from abc import ABC, abstractmethod

from arch import isRaspberryPI

logger = logging.getLogger('HALSensor')

irPIN = 4
pf = None if isRaspberryPI() else MockFactory()

class SensorTempl(ABC):
    def __init__(self, handler_in=None, handler_out=None):
        self.handler_in = handler_in
        self.handler_out = handler_out
        self.activated = False
        self.sensor = None

    def _sensor_handler_in(self):
        logger.info('IR sensor activated')
        try:
            if self.handler_in is not None:
                self.handler_in()
            else:
                logger.info('generic handler')
        except Exception:
            logger.exception('Exception handled module sensor')

    def _sensor_handler_out(self):
        logger.info('IR sensor de-activated')
        try:
            if self.handler_out is not None:
                self.handler_out()
            else:
                logger.info('generic handler')
        except Exception:
            logger.exception('Exception handled module sensor')


    def is_activated(self):
        return self.activated

    def set_handler_in(self,handler):
        self.handler_in = handler

    def set_handler_out(self,handler):
        self.handler_out = handler

    def release_handler_in(self):
        self.handler_in = None

    def release_handler_out(self):
        self.handler_out = None

    @abstractmethod
    def _close(self):
        ''' close instance '''
        raise NotImplementedError


##########################################
## Adafruit 3mm IRSensor
## https://www.adafruit.com/product/2167
##########################################
class AdafruitSensor(SensorTempl):
    def __init__(self, handler_in=None, handler_out=None):
        super().__init__(handler_in,handler_out)
        self.sensor = DigitalInputDevice(irPIN, pull_up=True, pin_factory=pf)
        self.sensor.when_activated = self._sensor_handler_in
        self.sensor.when_deactivated = self._sensor_handler_out

        if pf:
            import threading
            self.stop_event = threading.Event()
            self.thread = threading.Thread(target=self._mock_pin_thread, args=(self.stop_event,), daemon=True)
            self.thread.start()

    def _mock_pin_thread(self, stop_event):
        import pygame
        from pygame.locals import K_i
        while not stop_event.is_set():
          time.sleep(.01)
          keys = pygame.key.get_pressed()
          if keys[K_i]:
              self.sensor.pin.drive_low()
              time.sleep(.1)
          else:
              self.sensor.pin.drive_high()

    def is_activated(self):
        return self.sensor.is_active

    def _close(self):
        if pf:
            self.stop_event.set()
            time.sleep(.5)
        self.sensor.close()

#################################################
## Sparkfun IR receiver and emiter custom sensor
## https://www.sparkfun.com/products/241
#################################################
class SparkfunCustomIrSensor(SensorTempl):
    def __init__(self, handler_in=None, handler_out=None):
        super().__init__(handler_in,handler_out)
        self.sensor = DigitalInputDevice(irPIN, pull_up=True, pin_factory=pf)
        self.sensor.when_deactivated = self._sensor_handler_in
        self.sensor.when_activated = self._sensor_handler_out

        if pf:
            import threading
            self.stop_event = threading.Event()
            self.thread = threading.Thread(target=self._mock_pin_thread,args=(self.stop_event,),daemon=True)
            self.thread.start()

    def _mock_pin_thread(self, stop_event):
        import pygame
        from pygame.locals import K_i
        while not stop_event.is_set():
          time.sleep(.01)
          event = pygame.event.get(eventtype=pygame.KEYDOWN, pump=False)
          if event: print(event)
          keys = pygame.key.get_pressed()
          if keys[K_i]:
            self.sensor.pin.drive_high()
            time.sleep(.01)
          else:
            self.sensor.pin.drive_low()

    def is_activated(self):
        return not self.sensor.is_active

    def set_handler_in(self,handler):
        logger.info('IRSensor handler set')
        self.handler_in = handler

    def set_handler_out(self,handler):
        logger.info('IRSensor handler set')
        self.handler_out = handler

    def _close(self):
        if pf:
            self.stop_event.set()
            time.sleep(.5)
        self.sensor.close()


if __name__=='__main__':
    import pygame
    logging.basicConfig(filename='logs/sensortest.log', filemode='w+', level=logging.DEBUG,
            format='%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s',
            datefmt='%Y/%m/%d||%H:%M:%S'
            )
    logger.info('Sensors Test')
    pygame.init()
    screen = pygame.display.set_mode((300,300))
    time.sleep(1)
    def test_handler():
        print('IR handler')
        logger.info('testing handler')
    irbeam = AdafruitSensor()
    #irbeam = SparkfunCustomIrSensor()
    irbeam.set_handler_in(test_handler)

    from pygame.locals import K_s
    running = True
    while running:
        screen.fill((0,0,0))
        keys = pygame.key.get_pressed()
        if keys[K_s]:
            running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    print('finishing up')
    irbeam._close()
    print('ended')
