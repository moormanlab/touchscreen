'''
Hardware Abstraction Layer for Mice Touchscreen Project
'''

import time
import logging
import platform
logger = logging.getLogger('touchHAL')

buzzerPIN = 17
irPIN     = 23
valvePIN  = 26

RASPBERRY_PI = 0
PC           = 1
MACOS        = 2
LINUX_X86    = 3

def _getArch():
    platf = platform.uname()
    if platf[0] == 'Windows':
        return PC
    elif platf[0] == 'Linux':
        if platf[4].startswith('arm'):
            return RASPBERRY_PI
        elif platf[4].startswith('x86'):
            return LINUX_X86
        else:
            raise NameError('Linux architecture not supported')
    elif platf[0] == 'Darwin':
        return MACOS
    else:
        raise NameError('Architecture not recongnized')

#Checks if system is a Raspberry PI 
def isRaspberryPI():
    return (_getArch()==RASPBERRY_PI)

###########################
## Buzzer
###########################

class Buzzer():
    class _dummyBuzzer:
        def __init__(self):
            import pygame
            pygame.mixer.quit()
            pygame.mixer.init(44100, -16, 1)
            self.Fs = pygame.mixer.get_init()[0]
            self.amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1

    
        def play(self,frec=440.,duration=1.0):
            import pygame
            import math
            import array
            
            amp = self.amplitude
            if type(frec) == str:
                from gpiozero.tones import Tone
                f=Tone(frec)
                frec = float(f.real)
            elif type(frec) == int:
                frec = float(frec)
            elif frec == None:
                amp = 0
                frec= 440.0

            tau = 2*math.pi
            lT = int(duration*self.Fs)
            bufferSnd = array.array('h',[int(amp*math.sin(t*tau*frec/self.Fs)) for t in range(lT)])
            Tone=pygame.mixer.Sound(array=bufferSnd)
            Tone.play()
            logger.info('Dummy tone f={:4.4} Hz d={:4.4f}'.format(frec,duration))
            time.sleep(duration)


    class _piBuzzer:
        def __init__(self):
            from gpiozero import TonalBuzzer
            self.bz= TonalBuzzer(buzzerPIN)

        def play(self,frec=440.0,duration=1.0):
            from gpiozero.tones import Tone
            if type(frec) == float or type(frec)==int:
                t = Tone(float(frec))
            elif type(frec) == str:
                t = Tone(frec)
                frec = t.real
            else:
                t = frec
                frec = 0.
            logger.info('Buzzer Tone f={:4.3f}, d={:4.4f}'.format(frec,duration))
            self.bz.play(t)
            time.sleep(float(duration))
            self.bz.stop()

    __instance = None
    __arch = None
    
    def __init__(self):
        if Buzzer.__instance is None:
            Buzzer.__arch = _getArch()
            if Buzzer.__arch == RASPBERRY_PI:
                Buzzer.__instance=Buzzer._piBuzzer()
            else:
                Buzzer.__instance=Buzzer._dummyBuzzer()

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def play(self,frec=440.0,duration=1.0):
        return self.__instance.play(frec,duration)

    def playTune(self,tune):
        logger.info('Buzzer playing custom tune')
        for note, duration in tune:
            self.__instance.play(note,duration)

###########################
## IRSensor
###########################
class IRSensor(object):
    class _dummySensor(object):

        def __init__(self,handler=None):
            self.handler = handler
            self.time = 0
            self.pressed = False

            import threading
            self.thread = threading.Thread(target=self._dummyThread,daemon=True)
            self.thread.start()
            
        def _dummyThread(self):
            import pygame
            from pygame.locals import K_i
            dummyrun = True
            while dummyrun:
              time.sleep(.01)
              keys = pygame.key.get_pressed()
              if keys[K_i]:
                if not self.pressed:
                  self._sensorHandler()
                  self.pressed = True
                time.sleep(.01)
              else:
                if self.pressed:
                  self.pressed = False

        def _sensorHandler(self):
            logger.info('ir sensor activated')
            try:
                if self.handler is not None:
                    self.handler()
                else:
                    logger.info('generic handler')
            except Exception as e:
                logger.info('error handled module sensor')
                logger.info(e)

        def isPressed(self):
            return self.pressed

        def setHandler(self,handler):
            self.handler = handler

        def releaseHandler(self):
            self.handler = None

    class _piSensor:
        def __init__(self,handler=None):
            from gpiozero import Button
            self.handler = handler
            self.sensor = Button(irPIN)
            self.sensor.when_pressed = self._sensorHandler

        def _sensorHandler(self):
            logger.info('ir sensor activated')
            try:
                if self.handler is not None:
                    self.handler()
                else:
                    logger.info('generic handler')
            except Exception as e:
                logger.info('error handled module sensor')

        def isPressed(self):
            return self.sensor.is_pressed

        def setHandler(self,handler):
            logger.info('irsensor handler set')
            print('irsensor handler set')
            self.handler = handler

        def releaseHandler(self):
            self.handler = None

    __instance = None
    __arch = None

    def __init__(self,handler=None):
        if IRSensor.__instance is None:
            IRSensor.__arch = _getArch()
            if  IRSensor.__arch == RASPBERRY_PI:
                IRSensor.__instance=IRSensor._piSensor(handler)
            else:
                IRSensor.__instance=IRSensor._dummySensor(handler)
        else:
            if handler is not None:
                IRSensor.__instance.setHandler(handler)
            else:
                IRSensor.__instance.releaseHandler()

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def isPressed(self):
        return self.__instance.isPressed()

    def setHandler(self,handler):
        self.__instance.setHandler(handler)

    def releaseHandler(self):
        self.__instance.releaseHandler()

###########################
## Valve
###########################
class Valve(object):
    class _dummyValve:
        def __init__(self,openTime):
            logger.info('Using Dummy Valve')
            self.state = False
            self.openTime = openTime

        def close(self):
            self.state = False
        
        def open(self):
            self.state = True

        def drop(self):
            self.state = False

        def setOpenTime(self, openTime):
            self.openTime = openTime

        def getOpenTime(self):
            return self.openTime

        def isOpen(self):
            return self.state

    class _piValve:
        def __init__(self,openTime):
            from gpiozero import LED
            self.valve = LED(valvePIN)
            self.openTime = openTime

        def setOpenTime(self,openTime):
            self.openTime = openTime

        def getOpenTime(self):
            return self.openTime

        def isOpen(self):
            return self.valve.is_lit

        def open(self):
            self.valve.on()

        def close(self):
            self.valve.off()

        def drop(self):
            self.valve.blink(on_time=self.openTime,n=1)
            self.valve.off()

    __instance = None
    __arch = None

    def __init__(self,openTime=.4):
        if Valve.__instance is None:
            Valve.__arch = _getArch()
            if  Valve.__arch == RASPBERRY_PI:
                Valve.__instance=Valve._piValve(openTime)
            else:
                Valve.__instance=Valve._dummyValve(openTime)

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def setOpenTime(self,openTime):
        logger.info('Valve openTime {:.4f}'.format(openTime))
        return self.__instance.setOpenTime(openTime)

    def getOpenTime(self):
        return self.__instance.getOpenTime()

    def isOpen(self):
        return self.__instance.isOpen()

    def open(self):
        logger.info('Valve open')
        return self.__instance.open()

    def close(self):
        logger.info('Valve closed')
        return self.__instance.close()

    def drop(self):
        logger.info('Valve drop openTime {:.3f}'.format(self.openTime))
        return self.__instance.drop()

if __name__=='__main__':
    val = Valve()
    val.open()
    time.sleep(.5)
    val.close()
    val.setOpenTime(.2)
    val.drop()

    buzz = Buzzer()
    buzz.play(440,0.5)

    tune = [('C#4', 0.2), ('D4', 0.2), (None, 0.2),
            ('Eb4', 0.2), ('E4', 0.2), (None, 0.6),
            ('F#4', 0.2), ('G4', 0.2), (None, 0.6),
            ('Eb4', 0.2), ('E4', 0.2), (None, 0.2),
            ('F#4', 0.2), ('G4', 0.2), (None, 0.2),
            ('C4', 0.2), ('B4', 0.2), (None, 0.2),
            ('F#4', 0.2), ('G4', 0.2), (None, 0.2),
            ('B4', 0.2), ('Bb4', 0.5), (None, 0.6),
            ('A4', 0.2), ('G4', 0.2), ('E4', 0.2), 
            ('D4', 0.2), ('E4', 0.2)]

    buzz.playTune(tune)

    import pygame
    pygame.init()
    screen = pygame.display.set_mode((300,300))
    time.sleep(1)
    def testHandler():
        print('IR handler')
        logger.info('testing handler')
    irbeam = IRSensor()
    irbeam.setHandler(testHandler)

    running = True
    while running:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False
    pygame.quit()
