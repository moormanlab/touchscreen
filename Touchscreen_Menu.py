import pygame
import pygame_menu
# Importing Jason's behavioral test script
import mouse_touchscreen

# Initializes pygame
pygame.init()

#Creates surface width=800, height=400
surface = pygame.display.set_mode((800,400))

# Creates menu, adding title, and enabling touchscreen mode
menu = pygame_menu.Menu(400,800,'Mouse Touchscreen Menu', 
                        theme=pygame_menu.themes.THEME_GREEN, 
                        onclose=pygame_menu.events.RESET)

# Creates button for behavioral test 1
# Uses Jason's behavioral test script
menu.add_button('Behavioral Test 1', mouse_touchscreen.behavioral_test_1)

def behavioral_test_2():
    print('test 2 placeholder')
menu.add_button('Behavioral Test 2', behavioral_test_2)

def behavioral_test_3():
    print('test 3 placeholder')
menu.add_button('Behavioral Test 3', behavioral_test_3)

# Allows menu to be run
menu.mainloop(surface)





