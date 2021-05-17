import pygame
import time
import logging

SCREENWIDTH  = 800
SCREENHEIGHT = 480
CLOSINGBOXSIZE = 40
logger = logging.getLogger('retMenu')

def return_to_menu(event):
    try:
        closing = return_to_menu.closing
    except AttributeError:
        return_to_menu.closing = False
        closing = return_to_menu.closing
        logger.debug('First use of return_to_menu function. Setting closing variable')

    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN] and closing==False:
        logger.debug('Entering Closing step 1. Closing State = {}'.format(closing))
        position = getPosition(event)
        logger.debug(position)
        # Checks if screen was pressed in top left corner
        if (position[0] >= 0 and position[0] <= CLOSINGBOXSIZE) and position[1] >= 0 and position[1] <= CLOSINGBOXSIZE:
            return_to_menu.closing = True
            logger.debug('Hit closing area. new closing value {}'.format(not closing))
    elif event.type in [pygame.MOUSEBUTTONUP, pygame.FINGERUP] and closing==True:
        logger.debug('Entering Closing step 2. Closing State = {}'.format(closing))
        return_to_menu.closing = False
        position = getPosition(event)
        logger.debug(position)
        # Checks if screen was pressed in top right corner
        if (position[0] >= SCREENWIDTH-CLOSINGBOXSIZE and position[0] <= SCREENWIDTH) and position[1] >= 0 and position[1] <= CLOSINGBOXSIZE:
            logger.debug('Hit closing area 2. new closing value {}'.format(not closing))
            return True
        
    return False

def getPosition(event):
    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]:
        return event.pos
    elif event.type in [pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP]:
        return(int(event.x*SCREENWIDTH),int(event.y*SCREENHEIGHT))
    return (-1,-1)

