import pygame

SCREENWIDTH  = 800
SCREENHEIGHT = 480

POINTERPRESSED = 1
POINTERMOTION = 2
POINTERRELEASED = 3

tsColors = {
        'red':         ( 255,   0,   0),
        'green':       (   0, 255,   0),
        'blue':        (   0,   0, 255),
        'black':       (   0,   0,   0),
        'yellow':      ( 255, 255,   0),
        'purple':      ( 255,   0, 255),
        'white':       ( 255, 255, 255),
        'deepskyblue': (   0, 191, 255),
        'gray':        ( 128, 128, 128),
        'darkgray':    (  64,  64,  64),
        }

LOGSEP = '@@'

def getPosition(event):
    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]:
        return event.pos
    elif event.type in [pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP]:
        return(int(event.x*SCREENWIDTH),int(event.y*SCREENHEIGHT))
    return (-1,-1)

