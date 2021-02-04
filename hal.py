'''
Hardware Abstraction Layer for Mice Touchscreen Project
'''

import os
import time
import logging
logger = logging.getLogger('touchHAL')

buzzerPIN = 17 # 27 or 22
irPIN     = 23
valvePIN  = 25

RASPBERRY_PI = 0
PC           = 1
MACOS        = 2

def _getArch():
    arch = os.uname().machine
    if arch.startswith('arm'):
        return RASPBERRY_PI
    elif arch.startswith('x86') or arch.startswith('i686'):
        return PC
    else:
        return MAC

#Checks if system is a Raspberry PI 
def isRaspberryPI():
    return (_getArch()==RASPBERRY_PI)

###########################
## Buzzer
###########################
class _DummyBuzzer():
    def __init__(self):
        pass
    
    def play(self,seconds=1.0):
        time.sleep(seconds)

class Buzzer():
    def __init__(self):

        if _getArch() == RASPBERRY_PI:
            from gpiozero import TonalBuzzer
            self.arch = RASPBERRY_PI
            self.bz= TonalBuzzer(buzzerPIN)
        else:
            self.arch = PC
            self.bz = _DummyBuzzer()


    def play(self,seconds=1.0):
        if self.arch == RASPBERRY_PI:
            from gpiozero.tones import Tone
            self.bz.play(Tone(440.0))
            time.sleep(seconds)
            self.bz.stop()
        else:
            self.bz.play(1.0)


###########################
## IRSensor
###########################
class _DummySensor(object):
    def __init__(self):
        self.time = int(time.time())
    
    def isPressed(self):
        diff = int(time.time()) - self.time
        return (diff%2==0)


class IRSensor(object):
    def __init__(self,handler=None):
        self.handler = handler
        if _getArch() == RASPBERRY_PI:
            from gpiozero import Button
            self.arch = RASPBERRY_PI
            self.sensor = Button(irPIN)
            self.sensor.when_pressed = self._sensorHandler
        else:
            self.arch = PC
            self.sensor = _DummySensor()

    def _sensorHandler(self):
        try:
            print('generic handler')
            if self.handler is not None:
                self.handler()
        except Exception as e:
            logger.error(traceback.format_exc())
            print('error handled module sensor')

    def isPressed(self):
        return self.sensor.isPressed()


###########################
## Valve
###########################
class _DummyValve(object):
    def __init__(self):
        pass

    def off(self):
        pass
    
    def on(self):
        pass

    def blink(self,on_time=1.0,n=1):
        pass

class Valve(object):
    def __init__(self,openTime=.4):
        if _getArch() == RASPBERRY_PI:
            from gpiozero import LED
            self.arch = RASPBERRY_PI
            self.valve = LED(valvePIN)
        else:
            self.arch = PC
            self.valve = _DummyValve()
        self.openTime = openTime

    def setOpenTime(self,openTime):
        self.openTime = openTime

    def open(self):
        print('valve on')
        self.valve.on()

    def close(self):
        print('valve off')
        self.valve.off()

    def drop(self):
        print('valve drop')
        self.valve.blink(on_time=self.openTime,n=1)

