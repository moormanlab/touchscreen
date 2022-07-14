import pygame
import time
import logging

from .utils import SCREENWIDTH, SCREENHEIGHT, getPosition

CLOSINGBOXSIZE = 40
logger = logging.getLogger('retMenu')

def return_to_menu(event, closingBoxSize = CLOSINGBOXSIZE):
    try:
        assert isinstance(return_to_menu.closing, bool)
    except AttributeError:
        return_to_menu.closing = False
        logger.debug('First use of return_to_menu function. Setting variables')

    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN] and return_to_menu.closing==False:
        logger.debug('Entering Closing step 1. Closing State = {}'.format(return_to_menu.closing))
        position = getPosition(event)
        logger.debug(position)
        # Checks if screen was pressed in top left corner
        if position[0] >= 0 and position[0] <= closingBoxSize and \
           position[1] >= 0 and position[1] <= closingBoxSize:
            return_to_menu.closing = True
            logger.debug('Hit closing area. new closing value {}'.format(not return_to_menu.closing))
    elif event.type in [pygame.MOUSEBUTTONUP, pygame.FINGERUP] and return_to_menu.closing==True:
        logger.debug('Entering Closing step 2. Closing State = {}'.format(return_to_menu.closing))
        return_to_menu.closing = False
        position = getPosition(event)
        logger.debug(position)
        # Checks if screen was pressed in top right corner
        if position[0] >= SCREENWIDTH-closingBoxSize and position[0] <= SCREENWIDTH and \
           position[1] >= 0 and position[1] <= closingBoxSize:
            logger.debug('Hit closing area 2. new closing value {}'.format(not return_to_menu.closing))
            return True
        
    return False

