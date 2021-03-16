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
            self._arch = PC
            pass
    
        def play(self,frec=440.,duration=1.0):
            time.sleep(duration)

        def playTune(self,tune):
            self.bz.play(1.0)

    class _piBuzzer:
        def __init__(self):
            from gpiozero import TonalBuzzer
            self._arch = RASPBERRY_PI
            self.bz= TonalBuzzer(buzzerPIN)

        def play(self,frec=440.0,duration=1.0):
            from gpiozero.tones import Tone
            self.bz.play(Tone(float(frec)))
            time.sleep(float(duration))
            self.bz.stop()

        def playTune(self,tune):
            from gpiozero.tones import Tone
            for note, duration in tune:
                self.bz.play(note)
                time.sleep(float(duration))
            self.bz.stop()

    __instance = None

    def __init__(self):
        if Buzzer.__instance is None:

            if _getArch() == RASPBERRY_PI:
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
        return self.__instance.playTune(tune)

###########################
## IRSensor
###########################
class IRSensor(object):
    class _dummySensor(object):
        def __init__(self,handler=None):
            self.time = int(time.time())
        
        def isPressed(self):
            diff = int(time.time()) - self.time
            return (diff%2==0)

        def setHandler(self,handler):
            pass

        def releaseHandler(self):
            pass

    class _piSensor:
        def __init__(self,handler=None):
            from gpiozero import Button
            self.handler = handler
            self.arch = RASPBERRY_PI
            self.sensor = Button(irPIN)
            self.sensor.when_pressed = self._sensorHandler

        def _sensorHandler(self):
            try:
                if self.handler is not None:
                    self.handler()
                else:
                    logger.info('generic handler')
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.info('error handled module sensor')

        def isPressed(self):
            return self.sensor.is_pressed

        def setHandler(self,handler):
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

    def _sensorHandler(self):
        try:
            logger.info('generic handler')
            if self.handler is not None:
                self.handler()
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.info('error handled module sensor')

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def isPressed(self):
        return self.__instance.isPressed()

    def setHandler(self,handler):
        return self.__instance.setHandler(handler)

    def releaseHandler(self):
        return self.__instance.releaseHandler(handler)


###########################
## Valve
###########################
class Valve(object):
    class _dummyValve:
        def __init__(self):
            pass

        def off(self):
            pass
        
        def on(self):
            pass

        def drop(self):
            logger.info('valve drop computer')
            pass

        def setOpenTime(self, openTime):
            pass


    class _piValve:
        def __init__(self,openTime=.4):
            from gpiozero import LED
            self.valve = LED(valvePIN)
            self.openTime = openTime

        def setOpenTime(self,openTime):
            self.openTime = openTime

        def open(self):
            logger.info('valve on')
            self.valve.on()

        def close(self):
            logger.info('valve off')
            self.valve.off()

        def drop(self):
            logger.info('valve drop')
            self.valve.blink(on_time=self.openTime,n=1)

    __instance = None
    __arch = None

    def __init__(self):
        if Valve.__instance is None:
            Valve.__arch = _getArch()
            if  Valve.__arch == RASPBERRY_PI:
                Valve.__instance=Valve._piValve()
            else:
                Valve.__instance=Valve._dummyValve()

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def setOpenTime(self,openTime):
        return self.__instance.setOpenTime(openTime)

    def open(self):
        return self.__instance.open()

    def close(self):
        return self.__instance.close()

    def drop(self):
        return self.__instance.drop()

if __name__=='__main__':
#    val = Valve()
#    val.open()
#    time.sleep(.5)
#    val.close()
    buzz = Buzzer()
    buzz.play(440,0.5)
#
#    tune = [('C#4', 0.2), ('D4', 0.2), (None, 0.2),
#            ('Eb4', 0.2), ('E4', 0.2), (None, 0.6),
#            ('F#4', 0.2), ('G4', 0.2), (None, 0.6),
#            ('Eb4', 0.2), ('E4', 0.2), (None, 0.2),
#            ('F#4', 0.2), ('G4', 0.2), (None, 0.2),
#            ('C4', 0.2), ('B4', 0.2), (None, 0.2),
#            ('F#4', 0.2), ('G4', 0.2), (None, 0.2),
#            ('B4', 0.2), ('Bb4', 0.5), (None, 0.6),
#            ('A4', 0.2), ('G4', 0.2), ('E4', 0.2), 
#            ('D4', 0.2), ('E4', 0.2)]
#
#    buzz.playTune(tune)
