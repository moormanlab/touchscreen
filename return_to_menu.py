import pygame
import time
import logging

def return_to_menu(event,screen):
    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
        # Draws invisible box in top right corner to return to menu
        closing_box = pygame.draw.rect(screen, (0,0,0), (700,0, 100,100))
        # Checks if screen was pressed in top right corner
        curs_in_box = closing_box.collidepoint(pygame.mouse.get_pos())
        # Time elapsed since corner was pressed
        startTime = time.time()
        elapsed = 0
        # Checks time elapsed every second and closes program once 2 seconds have passed
        while curs_in_box:
            if elapsed > 2:
                return True
            # If corner is no longer being pressed, the loop breaks
            elif mouse_event_type() == False:
                break
            time.sleep(1)
            elapsed = time.time() - startTime
            logging.info('Top right corner pressed. Number of seconds elapsed: {:.2f}'.format(elapsed))
            curs_in_box = closing_box.collidepoint(pygame.mouse.get_pos())
        
    return False

def mouse_event_type():
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            return True
        else:
            return False
