import time
import logging
import gpiozero
from gpiozero.pins.mock import MockFactory
from abc import ABC, abstractmethod

from arch import isRaspberryPI

logger = logging.getLogger('HALSensor')

irPIN = 4
pf = None if isRaspberryPI() else MockFactory()

class SensorTempl(ABC):
    def __init__(self,handler=None):
        self.handler = handler
        self.activated = False
        self.sensor = None

    def _sensor_handler(self):
        logger.info('IR sensor activated')
        try:
            if self.handler is not None:
                self.handler()
            else:
                logger.info('generic handler')
        except Exception:
            logger.exception('Exception handled module sensor')


    def is_activated(self):
        return self.activated

    def set_handler(self,handler):
        self.handler = handler

    def release_handler(self):
        self.handler = None

    @abstractmethod
    def _close(self):
        ''' close instance '''
        raise NotImplementedError


##########################################
## Adafruit 3mm IRSensor
## https://www.adafruit.com/product/2167
##########################################
class AdafruitSensor(SensorTempl):
    def __init__(self,handler=None):
        super().__init__(handler)
        self.sensor = gpiozero.Button(irPIN, pin_factory=pf)
        self.sensor.when_pressed = self._sensor_handler

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
              print('key i pressed')
              self.sensor.pin.drive_low()
              time.sleep(.1)
          else:
              self.sensor.pin.drive_high()

    def is_activated(self):
        return self.sensor.is_pressed

    def set_handler(self,handler):
        logger.info('IRSensor handler set')
        self.handler = handler

    def _close(self):
        if pf:
            #print('closing adafruit')
            self.stop_event.set()
            time.sleep(.5)
        self.sensor.close()

#################################################
## Sparkfun IR receiver and emiter custom sensor
## https://www.sparkfun.com/products/241
#################################################
class SparkfunCustomIrSensor(SensorTempl):
    def __init__(self,handler=None):
        super().__init__(handler)
        self.sensor = gpiozero.Button(irPIN, pin_factory=pf)
        self.sensor.when_released = self._sensor_handler
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
          keys = pygame.key.get_pressed()
          if keys[K_i]:
            self.sensor.pin.drive_high()
            time.sleep(.01)
          else:
            self.sensor.pin.drive_low()

    def is_activated(self):
        return not self.sensor.is_pressed

    def set_handler(self,handler):
        logger.info('IRSensor handler set')
        self.handler = handler

    def _close(self):
        if pf:
            #print('closing sparkfun')
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
    #irbeam = DummyIRSensor()
    irbeam.set_handler(test_handler)

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
    #time.sleep(2)
    print('ended')
