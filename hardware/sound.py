import time
import logging
from gpiozero import TonalBuzzer, Buzzer, PWMOutputDevice 
from gpiozero.tones import Tone
from gpiozero.pins.mock import MockFactory, MockPWMPin
import pygame
import math
import array
import random
from abc import ABC, abstractmethod

from utils.arch import isRaspberryPI

TAU = 2*math.pi
pf = None if isRaspberryPI() else MockFactory(pin_class=MockPWMPin)

logger = logging.getLogger('halSound')

#audioPin = 17
buzzerPIN = 12

class tTone(object):
    def __init__(self, frequency: int, duration: float = 1.0, amplitude: float = 1.0):
        self.frequency = int(frequency)
        self.duration = float(duration)
        amp = float(amplitude)
        if amp >= 0 and amp <= 1.0:
            self.amplitude = amp
        else:
            self.amplitude = 1.0

    def get_amplitude(self) -> float:
        return self.amplitude

    def get_frequency(self) -> int:
        return self.frequency

    def get_duration(self) -> float:
        return self.duration

    def __str__(self) -> str:
        msg = ''
        if self.frequency > 1000:
            msg += 'frequency = {:3.2f} kHz, '.format(self.frequency)
        else:
            msg += 'frequency = {:d} Hz, '.format(self.frequency)
        if self.duration < 1.0:
            msg += 'duration = {:d} ms, '.format(int(self.duration*1000))
        else:
            msg += 'duration = {:3.1f} s, '.format(self.duration)
        msg += 'amplitude = {:d} %'.format(int(self.amplitude*100))
        return msg

class AudioDevTemplate(ABC):
    def __init__(self):
        pygame.mixer.quit()
        pygame.mixer.init(44100, -16, 1)
        self.Fs = pygame.mixer.get_init()[0]
        self.max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
        self.amplitude = 1.0

    def play(self, tone: tTone = None, frequency: int = 440, duration: float = 1.0, amplitude: float = 1.0):
        amp = self.amplitude * self.max_amplitude

        if not (tone and isinstance(tone,tTone)):
            if type(tone) == int:
                frequency = tone
            tone = tTone(frequency, duration, amplitude)

        amplitude = amp * tone.get_amplitude()
        frequency = tone.get_frequency()
        duration = tone.get_duration()

        lT = int(duration*self.Fs)
        bufferSnd = array.array('h',[int(amplitude*math.sin(t*TAU*frequency/self.Fs)) for t in range(lT)])
        ptone=pygame.mixer.Sound(array=bufferSnd)
        ptone.play()
        logger.info('Playing Tone '.format(tone))
        time.sleep(duration)

    def noise(self,duration=1.0):
        
        amp = self.amplitude * self.max_amplitude

        lT = int(duration*self.Fs)
        bufferSnd = array.array('h',[int(amp*max(-1,min(1,random.gauss(0,1)))) for t in range(lT)])
        noise=pygame.mixer.Sound(array=bufferSnd)
        noise.play()
        logger.info('Playing noise duration = {:4.1f} s'.format(duration))
        time.sleep(duration)

    def set_amplitude(self, amplitude: float) -> None:
        if amplitude >=0 and amplitude <=1.0:
            self.amplitude = amplitude
    
    @abstractmethod
    def _close(self):
        ''' close instance '''
        raise NotImplementedError


######################################################
## Buzzer
## https://www.sparkfun.com/products/7950
######################################################
class SparkFunBuzzer(AudioDevTemplate):
    def __init__(self):
        self.bz =  PWMOutputDevice(buzzerPIN, pin_factory = pf)

    def play(self, tone: tTone = None, frequency: int = 440, duration: float = 1.0, amplitude: float = 1.0):
        if not (tone and isinstance(tone,tTone)):
            if type(tone) == int:
                frequency = tone
        else:
            frequency = tone.get_frequency()
            duration = tone.get_duration()
            amplityde = tone.get_amplitude()
        self.bz.frequency = frequency
        logger.info('Buzzer Tone frequency = {:4.3f}, duration = {:4.4f}'.format(frequency,duration))
        self.bz.value = .5*amplitude
        time.sleep(float(duration))
        self.bz.value = 0

    def playTune(self,tune):
        logger.info('Buzzer playing custom tune')
        for note, duration in tune:
            self.play(frequency=note,duration=duration)

    def _close(self):
        self.bz.close()
        
######################################################
## Speaker
## https://www.sparkfun.com/products/11089
## https://www.digikey.com/en/products/detail/cui-devices/CMS-151125-078L100/8581913
######################################################
class CustomSpeaker(AudioDevTemplate):
    def __init__(self):
        super().__init__()

    def playTune(self,tune):
        logger.info('Custom Speaker playing custom tune')
        for note, duration in tune:
            self.play(frequency=note, duration=duration)

    def _close(self):
        pass


if __name__=='__main__':
    logging.basicConfig(filename='soundtest.log', filemode='w+', level=logging.DEBUG,
            format='%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s',
            datefmt='%Y/%m/%d||%H:%M:%S'
            )
    logger.info('Sound Test')
    buzz = SparkFunBuzzer()
    #buzz = CustomSpeaker()

    buzz.play(1000,duration=2.0)
    buzz.set_amplitude(.3)

    time.sleep(1)

    t1 = tTone(frequency = 1000, duration=1.0)
    t2 = tTone(frequency = 1000, duration=1.0, amplitude=.1)
    buzz.play(t1)
    time.sleep(1)

    buzz.play(t2)
    time.sleep(1)
    print(t1)
    print(t2)

    tunestr = [('C#4', 0.2), ('D4', 0.2), (None, 0.2),
            ('Eb4', 0.2), ('E4', 0.2), (None, 0.6),
            ('F#4', 0.2), ('G4', 0.2), (None, 0.6),
            ('Eb4', 0.2), ('E4', 0.2), (None, 0.2),
            ('F#4', 0.2), ('G4', 0.2), (None, 0.2),
            ('C4', 0.2), ('B4', 0.2), (None, 0.2),
            ('F#4', 0.2), ('G4', 0.2), (None, 0.2),
            ('B4', 0.2), ('Bb4', 0.5), (None, 0.6),
            ('A4', 0.2), ('G4', 0.2), ('E4', 0.2), 
            ('D4', 0.2), ('E4', 0.2)]

    tune = []
    for tone in tunestr:
        t = Tone(tone[0]).real if tone[0] else 0
        tune.append((int(t), tone[1]))

    buzz.playTune(tune)

    time.sleep(1)

    buzz.noise(2)
