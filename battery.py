import serial
import re
from gpiozero import DigitalInputDevice
from gpiozero.pins.mock import MockFactory
import subprocess
import time
import threading
import logging
from abc import ABC, abstractmethod

from arch import isRaspberryPI

logger = logging.getLogger('HALBattery')
DEFAULTPORT = '/dev/serial0'
DEFAULTIOPIN = 17

pf = None if isRaspberryPI() else MockFactory()

class BatteryTemplate(ABC):
    def __init__(self):
        self.connected = False
        self.powered = False
        self.vout = 0
        self.capacity = 0
        self.version = None
        self.lt = threading.Thread(target = self._log_thread, daemon=True)
        self.ut = threading.Thread(target = self._update_thread, daemon=True)
    
    def log_data(self):
        if self.connected:
            logger.info('Capacity = {}, powered = {}, vout = {}'.format(self.capacity,self.powered,self.vout))
        else:
            logger.info('Battery not connected')

    def _log_thread(self):
        while self.connected:
            self.log_data()
            time.sleep(60)

    def update_data(self):
        '''
            return True if update was successful
        '''
        return True

    def _update_thread(self):
        while self.connected:
            power = self.powered
            self.update_data()
            if self.powered == (not power):
                self.log_data()
            time.sleep(5)

    def _close(self):
        ''' close instance '''
        raise NotImplementedError

    def get_version(self):
        if self.connected:
            return self.version
        else:
            return None

    def get_powered(self):
        if self.connected:
            return self.powered
        else:
            return None

    def get_capacity(self):
        if self.connected:
            return self.capacity
        else:
            return None

    def get_outputV(self):
        if self.connected:
            return self.vout
        else:
            return None


#################################################
# Battery controler Tpi UPSPack Standard V3P
# version 3.2P
# https://github.com/rcdrones/UPSPACK_V3
#################################################
class UPSV3P2Bat(BatteryTemplate):
    def __init__(self, port = DEFAULTPORT, speed = 9600, gpioPIN = DEFAULTIOPIN):
        super().__init__()
        self.port = port
        self.speed = speed
        self.gpioPIN = gpioPIN
        self.serial = None
        self.gpio = DigitalInputDevice(self.gpioPIN, pin_factory=pf)#, pull_up=None, active_state = True)
        self._lock = threading.Lock()
        if pf:
            print('Mock pin')
            self.stop_event = threading.Event()
            self.disconnet = threading.Event()
            self.mt = threading.Thread(target = self._mock_pin_thread, args=(self.stop_event,), daemon=True)
    
    def update_data(self):
        with self._lock:
            if pf:
                # Mocking update
                if not self.disconnet.is_set():
                    import random
                    self.capacity = random.randint(0,100)
                    self.powered = True if random.random() > 0.5 else False
                    return True
                else:
                    logger.debug('Battery connection data corrupted, disconnecting')
                    self.connected = False
                    self.disconnet.clear()
                    self.gpio.when_activated = None
                    logger.debug('Shutdown check disabled')
                    return False

            try:
                data = ''
                while self.serial.inWaiting() > 4000:
                    tmp = self.serial.read(4000)
                a = 10
                while self.serial.inWaiting() < 100:
                    if a == 10:
                        b = self.serial.inWaiting()
                    if a == 0:
                        if self.serial.inWaiting() == b:
                            raise ValueError('No data waiting to be readed')
                        else:
                            a = 10
                    time.sleep(.1)
                    a -= 1
                uart_string = self.serial.read(self.serial.inWaiting())
                data = uart_string.decode('ascii','ignore')

                result = re.findall('\$ (.*?) \$',data)[-1]
            except:
                logger.exception('Battery connection data corrupted, disconnecting')
                logger.debug(data)
                self.gpio.when_activated = None
                logger.debug('Shutdown check disabled')
                self.connected = False
                return False

            self.version = re.findall(r'SmartUPS (.*?),',result)[0]
            tmp = re.findall(r',Vin (.*?),',result)[0]
            self.powered = True if tmp == 'GOOD' else False
            self.capacity = int(re.findall(r'BATCAP (.*?),',result)[0])
            self.vout = re.findall(r',Vout (.*)',result)[0]

            return True

    def _shutdown_check(self):
        logger.debug('Entering Shutdown Check')
        a = 0
        if self.gpio.is_active:
            while self.gpio.is_active:
                b = self.gpio.active_time
                if b:
                    a = b
                time.sleep(0.0001)
                if a > 1:
                    break

        logger.info('Battery shutdown pin was high for {:d} ms'.format(round(a*1000)))
        logger.debug('Battery shutdown pin was high for {:2.5f} s'.format(a))
        if a > 0.001 and a < 0.03:
            logger.info('Detected LOW battery capacity, System will shutdown')
            self.log_data()
            logger.debug('Shutting down')
            self.connected = False
            if pf:
                print('Fake shutdown')
                self.stop_event.set()
                import pygame
                pygame.quit()
            else:
                subprocess.call(['sudo', 'sync'])
                time.sleep(1)
                subprocess.call(['sudo', 'shutdown', 'now'])
            

    def detect_battery(self):
        if not self.connected:
            if pf:
                # Mocking detection
                self.connected = True
                self.powered = True
                self.vout = 5250
                self.capacity = 100
                self.version = 'Mock UPSV3P2'
                self.disconnet = threading.Event()
                self.lt = threading.Thread(target = self._log_thread,daemon=True)
                self.ut = threading.Thread(target = self._update_thread,daemon=True)
                self.lt.start()
                self.ut.start()
                self.gpio.when_activated = self._shutdown_check
                if pf:
                    print('Setting mock pin thread')
                    if not self.mt.is_alive():
                        self.mt.start()
                        print('Mock pin thread started')

            else:
                try:
                    self.serial = serial.Serial(self.port, self.speed)
                    self.serial.flushInput()
                    self.serial.timeout = 5
                    self.update_data()
                    if self.version:
                        logger.debug('Battery detected')
                        self.connected = True
                        self.lt = threading.Thread(target = self._log_thread,daemon=True)
                        self.ut = threading.Thread(target = self._update_thread,daemon=True)
                        self.lt.start()
                        self.ut.start()
                        self.gpio.when_activated = self._shutdown_check
                        logger.debug('Shutdown check enabled')

                except serial.SerialException:
                    logger.exception('No serial port {} available'.format(self.port))
                except IndexError:
                    logger.exception('Battery not detected')

        return self.connected

    def _mock_pin_thread(self, stop_event):
        import pygame
        from pygame.locals import K_p, K_d
        while True:
            time.sleep(.01)
            if not stop_event.is_set():
                keys = pygame.key.get_pressed()
                if keys[K_p]:
                  print('Emulating low battery signal')
                  tt = threading.Thread(target=self._fake_trigger, daemon = True)
                  tt.start()
                  self.gpio.pin.drive_high()
                  time.sleep(1)
                elif keys[K_d]:
                  print('Emulating disconnection')
                  self.disconnet.set()
                  time.sleep(.1)
                else:
                  if stop_event.is_set():
                      print('strange')
            else:
                print('Mock pin thread stopped')
                break

    def _fake_trigger(self):
        time.sleep(.02)
        self.gpio.pin.drive_low()
        return

    def _close(self):
        self.connected = False
        if pf:
            self.stop_event.set()
            time.sleep(.2)
        else:
            self.serial.close()
        self.gpio.close()


if __name__ == '__main__':
    import pygame
    from pygame.locals import K_ESCAPE, KEYDOWN, QUIT
    pygame.init()
    screen = pygame.display.set_mode((300,300))
    logging.basicConfig(filename='logs/battery.log', filemode='w+', level=logging.DEBUG,
            format='%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s',
            datefmt='%Y/%m/%d||%H:%M:%S'
            )
    logger.info('Battery Test')
    bat = UPSV3P2Bat()
    logger.info('Battery detected {}'.format(bat.detect_battery()))
    running = True
    i = 0
    while running:
        if bat.get_version():
            if i == 100:
                i = 0
                print('Waiting for shutdown. Cap = {} %'.format(bat.get_capacity()))
        else:
            print('Disconnected, trying to reconnect')
            time.sleep(10)
            bat.detect_battery()

        time.sleep(0.05)
        i += 1
        
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    running = False
        except:
            running = False
    bat._close()
    pygame.quit()
    time.sleep(1)
