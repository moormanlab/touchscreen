import time
import logging
from gpiozero import DigitalOutputDevice
from gpiozero.pins.mock import MockFactory
from abc import ABC, abstractmethod

from arch import isRaspberryPI

logger = logging.getLogger('halLiqReward')

pf = None if isRaspberryPI() else MockFactory()

liqRewPIN  = 26

class LiquidRewardTempl(ABC):
    def __init__(self, drop_amount: int = 1):
        self.drop_amount = drop_amount

    @abstractmethod
    def is_open(self) -> bool:
        ''' return True if the reward is continusly running ''' 
        raise NotImplementedError

    @abstractmethod
    def open(self):
        ''' give continously liquid reward ''' 
        raise NotImplementedError

    @abstractmethod
    def close(self):
        ''' stop giving continously liquid reward ''' 
        raise NotImplementedError

    @abstractmethod
    def drop(self):
        ''' release drop_amount of liquid reward ''' 
        raise NotImplementedError

    @abstractmethod
    def set_drop_amount(self, amount: int):
        ''' define the amount of reward ''' 
        raise NotImplementedError

    @abstractmethod
    def get_drop_amount(self):
        ''' return the amount of reward ''' 
        raise NotImplementedError

    @abstractmethod
    def _close(self):
        ''' close instance '''
        raise NotImplementedError

    def __str__(self):
        return 'Drop Amount {:d}'.format(self.drop_amount)

#####################################################
## Lee Valve
#####################################################
class LeeValve(LiquidRewardTempl):
    def __init__(self, drop_amount: int = 1):
        #super().__init__()
        #super().__init__(drop_amount)
        self.valve = DigitalOutputDevice(liqRewPIN, pin_factory=pf)
        self.set_drop_amount(drop_amount)

    def set_drop_amount(self, drop_amount: int):
        ''' the drop amount is a multiple of 10 ms '''
        self.open_time = float(0.01*drop_amount)

    def get_drop_amount(self) -> int:
        return int(self.open_time/0.01)

    def is_open(self):
        return self.valve.value == 1

    def open(self):
        self.valve.on()

    def close(self):
        self.valve.off()

    def drop(self):
        self.valve.blink(on_time=self.open_time, n=1)

    def _close(self):
        self.valve.close()

    def __str__(self):
        return 'Drop open time:  {:03d} ms'.format(self.get_drop_amount()*10)

#####################################################
## Lee Pump 12/24 V micro dose
#####################################################
class LeePump(LiquidRewardTempl):
    def __init__(self, drop_amount: int = 1):
        super().__init__(drop_amount)
        self.pump = DigitalOutputDevice(liqRewPIN, pin_factory=pf)

    def set_drop_amount(self, drop_amount: int):
        self.drop_amount = drop_amount

    def get_drop_amount(self):
        return self.drop_amount

    def is_open(self):
        return self.pump.value == 1

    def open(self):
        self.pump.blink(on_time=.1, off_time=.1, background=True)

    def close(self):
        self.pump.off()

    def drop(self):
        self.pump.blink(on_time=.1, off_time=.1, n=self.drop_amount, background=True)

    def _close(self):
        self.pump.close()

    def __str__(self):
        return 'Drop amount:  {:03d} ul'.format(self.drop_amount*10)

if __name__=='__main__':
    logging.basicConfig(filename='logs/liqrewtest.log', filemode='w+', level=logging.DEBUG,
            format='%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s',
            datefmt='%Y/%m/%d||%H:%M:%S'
            )
    logger.info('Liquid Reward Test')
    val = LeeValve()
    val.open()
    time.sleep(.5)
    val.close()
    val.set_drop_amount(2)
    val.drop()
    print('a b a {}'.format(val))
    val._close()

    pump = LeePump()
    pump.open()
    time.sleep(5)
    pump.close()
    pump.set_drop_amount(2)
    pump.drop()
    print('a b a {}'.format(pump))
    pump._close()

    pump = LeePump2()
    pump.open()
    time.sleep(5)
    pump.close()
    pump.set_drop_amount(2)
    pump.drop()
    print('a b a {}'.format(pump))
    pump._close()


