import platform

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
            raise NameError('Linux architecture not recognized')
    elif platf[0] == 'Darwin':
        return MACOS
    else:
        raise NameError('Architecture not recognized')

#Checks if system is a Raspberry PI 
def isRaspberryPI():
    return (_getArch()==RASPBERRY_PI)
