'''
Hardware Abstraction Layer for Mice Touchscreen Project
'''

import time
import logging
import gpiozero

from arch import isRaspberryPI

logger = logging.getLogger('touchHAL')

'''
gpio pins used by different hardware

audio:
buzzer   (flexible): 12 (+), GND (-) 
speakers (fixed): (3.5 mm audio jack)
audiohat (fixed): 2 (i2c sda), 3 (i2c scl), 25 (led), 19 (i2s lrclk), 18 (i2s clk), 20 (i2s adc), 21 (i2s dac), 23 (button)

sensors:
adafruit/sparkfun (flexible): 3.3V, GND, 4 (input)

battery:
UPSV3P2 (fixed/flexible): 5V, GND, 8 (UART txd), 10 (uart rxd) / 17 (shutdown input)

liquid reward:
valve/pump (flexible): 5V, GND, 26 (output)

food reward:
(flexible): 16 (output)
'''


########################################
## Sound
########################################
from sound import SparkFunBuzzer, CustomSpeaker
class Sound():

    __instance = None
    __variant = None
    __items = [('No Audio', 'None'),('Buzzer', 'spkfbuzzer'),('Speaker','custspk')]
    
    def __init__(self, variant=None):
        '''
            if there is no instance create one.
            if no variant specified or using PC, use a dummy
            if already is an instance and specifying a new variant 
            (only should happen during hardware configuration)
            close old instance and create the new one.
        '''
        if Sound.__instance and variant is not None:
            logger.debug('Closing Sound instance {}'.format(Sound.__variant))
            Sound.__instance._close()
            Sound.__instance = None
            Sound.__variant = None

        if Sound.__instance is None:
            if variant is not None:
                if variant == 'spkfbuzzer':
                    Sound.__instance = SparkFunBuzzer()
                elif variant == 'custspk':
                    Sound.__instance = CustomSpeaker()
                else:
                    raise ValueError('Audio device "{}" not recognized'.format(variant))
                Sound.__variant = variant
            else:
                raise ValueError('Audio device not specified')
            logger.debug('New sound instance {}'.format(Sound.__variant))


    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def get_type(self):
        return self.__variant

    def get_items():
        return Sound.__items

########################################
## IR Reward Sensor
########################################
from sensor import AdafruitSensor, SparkfunCustomIrSensor
class IRSensor(object):

    __instance = None
    __variant = None
    __items = [('No Sensor', 'None'),('AdaFruit', 'adafruit'),('SparkfunCustom','sparkfuncustom')]

    def __init__(self,handler_in=None,handler_out=None,variant=None):
        ''' 
            if there is already an instance and specifying a (new) variant (only should happen during hardware configuration) close old instance and create the new one.
            if there is no instance create one.
            if no variant specified or using PC, use a dummy
            if no variant specified and there is already an instance, just set or release handler
        '''
        if IRSensor.__instance and variant is not None:
            logger.debug('Closing IRSensor instance {}'.format(IRSensor.__variant))
            IRSensor.__instance._close()
            IRSensor.__instance = None
            IRSensor.__variant = None

        if IRSensor.__instance is None:
            if variant is not None:
                if variant == 'adafruit':
                    IRSensor.__instance=AdafruitSensor(handler_in,handler_out)
                elif variant == 'sparkfuncustom':
                    IRSensor.__instance=SparkfunCustomIrSensor(handler_in,handler_out)
                else:
                    raise ValueError('Sensor device "{}" not recognized'.format(variant))
                IRSensor.__variant = variant
            else:
                raise ValueError('Sensor device not specified')

            logger.debug('New IRSensor instance {}'.format(IRSensor.__variant))
        else:
            if handler_in is not None:
                IRSensor.__instance.set_handler_in(handler_in)
            else:
                IRSensor.__instance.release_handler_out()
            if handler_out is not None:
                IRSensor.__instance.set_handler_out(handler_out)
            else:
                IRSensor.__instance.release_handler_out()

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def is_activated(self):
        if IRSensor.__instance:
            return IRSensor.__instance.is_activated()
        else:
            return False

    def get_type(self):
        return self.__variant

    def get_items():
        return IRSensor.__items

########################################
## Liquid Reward
########################################
from liqrew import LeeValve, LeePump

class LiqReward(object):
    __instance = None
    __variant = None
    __items = [('No Liquid Reward', 'None'),('Valve', 'leevalve'),('Pump','leepump')]

    def __init__(self, drop_amount: int = 1, variant: str = None):
        ''' if there is no instance create one.
            if no variant specified or using PC, use a dummy
            if already is an instance and specifying a new variant 
            (only should happen during hardware configuration)
            close old instance and create the new one.
        '''
        if LiqReward.__instance and variant is not None:
            logger.debug('Closing Liquid Reward instance {}'.format(LiqReward.__variant))
            LiqReward.__instance._close()
            LiqReward.__instance = None
            LiqReward.__variant = None

        if LiqReward.__instance is None:
            if variant is not None:
                if variant == 'leevalve':
                    LiqReward.__instance = LeeValve(drop_amount)
                elif variant == 'leepump':
                    LiqReward.__instance = LeePump(drop_amount)
                else:
                    raise ValueError('Liquid Reward Device "{}" not recognized'.format(variant))
                LiqReward.__variant = variant
            else:
                raise ValueError('Liquid Reward Variant needs to be specified')
            logger.debug('New Liquid Reward instance {}'.format(LiqReward.__variant))


    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def __str__(self):
        if LiqReward.__instance:
            return self.__instance.__str__()
        else:
            return 'No liqreward instance'

    def set_drop_amount(self, drop_amount: int):
        if LiqReward.__instance:
            logger.info('Liquid Reward drop amount {:d}'.format(drop_amount))
            return LiqReward.__instance.set_drop_amount(drop_amount)

    def get_drop_amount(self):
        if LiqReward.__instance:
            return LiqReward.__instance.get_drop_amount()

    def is_open(self):
        if LiqReward.__instance:
            return LiqReward.__instance.is_open()

    def open(self):
        if LiqReward.__instance:
            logger.info('Valve open')
            return LiqReward.__instance.open()

    def close(self):
        if LiqReward.__instance:
            logger.info('Valve closed')
            return LiqReward.__instance.close()

    def drop(self):
        if LiqReward.__instance:
            logger.info('Valve drop amount {}'.format(repr(LiqReward.__instance)))
            return LiqReward.__instance.drop()

    def get_type(self):
        return LiqReward.__variant

    def get_items():
        return LiqReward.__items

############
# Battery
############
from battery import UPSV3P2Bat

class Battery(object):
    __instance = None
    __variant = None
    
    def __init__(self, variant = None):
        if Battery.__instance is None:
            Battery.__instance = UPSV3P2Bat()
            logger.debug('New battery instance created')

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def disconnect(self):
        if Battery.__instance:
            Battery.__instance._close()
            Battery.__instance = None

if __name__=='__main__':
    logging.basicConfig(filename='logs/haltest.log', filemode='w+', level=logging.DEBUG,
            format='%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s',
            datefmt='%Y/%m/%d||%H:%M:%S'
            )
    logger.info('HAL Test')
    val = LiqReward()
    val.open()
    time.sleep(.5)
    val.close()
    val.setOpenTime(.2)
    val.drop()

    buzz = Sound()
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
    irbeam.set_handler(testHandler)

    running = True
    while running:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False
    pygame.quit()
