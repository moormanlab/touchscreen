# # pylint: disable=import-error
# import pygame
# import pygame_vkeyboard as vkboard
# # pylint: enable=import-error


# surface.fill((20,100,100))

# layout = VKeyboardLayout(VKeyboardLayout.QWERTY)
# keyboard = VKeyboard(surface, on_key_event, layout, show_text = True, joystick_navigation=True)

# clock = pygame.time.Clock()

# # Main loop
# while True:
#     clock.tick(100)  # Ensure not exceed 100 FPS

#     events = pygame.event.get()

#     for event in events:
#         if event.type == pygame.QUIT:
#             print("Average FPS: ", clock.get_fps())
#             exit()

#     keyboard.update(events)
#     rects = keyboard.draw(surface)

#     # Flip only the updated area
#     pygame.display.update(rects)
