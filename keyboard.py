import pygame
from pygame_vkeyboard import vkeys
from pygame_vkeyboard import vkeyboard as vkb
import time

last_time = time.time_ns()

class VEnterKey(vkeys.VActionKey):
    """Action key for the uppercase switch. """

    def __init__(self, action, state_holder, length=1):
        super().__init__(action,
                         state_holder,
                         u'\u2611',  #263a  2714 2705 2713
                         u'\u2611')#'SET')

        self.length = length

    def is_activated(self):
        """Indicates if this key is activated.

        Returns
        -------
        is_activated: bool
            True if activated, False otherwise.
        """
        return False

    def set_size(self, width, height):
        """Sets the size of this key.

        Parameters
        ----------
        width:
            Background width.
        height:
            Background height.
        """
        super().set_size(width * self.length, height)


class VCancelKey(vkeys.VActionKey):
    """Action key for the uppercase switch. """

    def __init__(self, action, state_holder, length=1):
        super().__init__(action,
                         state_holder,
                         u'\u2612',  #2297  2327  2612 (2611 enter)  2716 (2714 enter)  2715 (2713 enter)  2bbd-bf
                         u'\u2297')#'SET')
        #self.value = pygame.K_KP_ENTER
        self.length = length

    def is_activated(self):
        """Indicates if this key is activated.

        Returns
        -------
        is_activated: bool
            True if activated, False otherwise.
        """
        return False

    def set_size(self, width, height):
        """Sets the size of this key.

        Parameters
        ----------
        width:
            Background width.
        height:
            Background height.
        """
        super().set_size(width * self.length, height)

class VClearKey(vkeys.VActionKey):
    """Action key for clearing the buffer. """

    def __init__(self, action, state_holder, length=2):
        super(VClearKey, self).__init__(action,
                                        state_holder,
                                        u'\u232b',#u'\u2297', 2716
                                        u'\u232b')#'CLEAR')
        #vkeys.VKey.__init__(self, u'\x7f', u'\u232b')  #u'\u232b',#u'\u2297', 2716
# 2302  para shift  2716 para clear
        #self.value = 'del'
        self.length = length

    def is_activated(self):
        """Indicates if this key is activated.

        Returns
        -------
        is_activated: bool
            True if activated, False otherwise.
        """
        return False

    def set_size(self, width, height):
        """Sets the size of this key.

        Parameters
        ----------
        width:
            Background width.
        height:
            Background height.
        """
        super(VClearKey, self).set_size(width * self.length, height)

    def update_buffer(self, string):
        """Do not update text but trigger the delegate action.

        Parameters
        ----------
        string:
            Not used, just to match parent interface.

        Returns
        -------
        string:
            Empty string to clear buffer.
        """
        return ''

class customVKLayout(vkb.VKeyboardLayout):
    def __init__(self,model):
        self.position = None
        self.size = None
        self.rows = []
        self.sprites = pygame.sprite.LayeredDirty()
        self.key_size = None
        self.padding = 5
        self.height_ratio = .86
        self.selection = None
        self.allow_space = True
        self.allow_uppercase = True
        self.allow_special_chars = False
        for model_row in model:
            row = vkb.VKeyRow()
            for value in model_row:
                key = vkeys.VKey(value)
                row.add_key(key)
                self.sprites.add(key, layer=1)
            self.rows.append(row)
        self.max_length = len(max(self.rows, key=len))
        if self.max_length == 0:
            raise ValueError('Empty layout model provided')
        if self.height_ratio is not None and (self.height_ratio < 0.2 or self.height_ratio > 1):
            raise ValueError('Surface height ratio shall be from 0.2 to 1')


    def configure_special_keys(self, keyboard):
        """Configures specials key if needed.

        Parameters
        ----------
        keyboard:
            Keyboard instance this layout belong.
        """
        special_row = vkb.VKeyRow()
        max_length = self.max_length

        # Create special keys list
        special_keys = []
        special_keys.append(vkeys.VUppercaseKey(keyboard.on_uppercase, keyboard))
        special_keys.append(vkeys.VSpaceKey(length=4))
        special_keys.append(vkeys.VBackKey())
        special_keys.append(VClearKey(keyboard.clear_text, keyboard))
        special_keys.append(VEnterKey(keyboard.enter_text, keyboard))
        special_keys.append(VCancelKey(keyboard.cancel, keyboard))
        self.sprites.add(*special_keys, layer=1)

        # Dispatch special keys in the layout
        while len(special_keys):
            special_row.add_key(special_keys.pop(0))

        # Adding left to the special bar.
        self.rows.append(special_row)



    def set_size(self, size, surface_size):
        """Sets the size of this layout, and updates
        position, and rows accordingly.

        Parameters
        ----------
        size:
            Size of this layout.
        surface_size:
            Target surface size on which layout will be displayed.
        """
        self.size = size
        self.position = (0, surface_size[1] - self.size[1])

        y = self.position[1] + (self.size[1] - len(self.rows) * self.key_size
                                - (len(self.rows) + 1) * self.padding) // 2
        y += self.padding
        for row in self.rows:
            nb_keys = len(row)
            width = (nb_keys * self.key_size) + ((nb_keys + 1) * self.padding)
            x = (surface_size[0] - width) // 2 + self.padding
            if row.space:
                # added a +1 to compensate for the length 2 in clear button
                x -= ((row.space.length - 1 + 1) * self.key_size) / 2
            row.set_size((x, y), self.key_size, self.padding)
            y += self.padding + self.key_size


class customVKeyboard(vkb.VKeyboard):
    def __init__(self,
                 surface,
                 main_layout,
                 renderer):
        super().__init__(surface=surface,
                         text_consumer=None,
                         main_layout=main_layout,
                         show_text=True,
                         joystick_navigation=False,
                         renderer=renderer,
                         special_char_layout=None)

    def on_key_down(self, key):
        """Process key down event by pressing the given key.

        Parameters
        ----------
        key:
            Key that receives the key down event.
        """
        global last_time
        if time.time_ns() - last_time > 1000000:
            if isinstance(key, vkeys.VBackKey):
                self.input.delete_at_cursor()
            else:
                text = key.update_buffer('')
                if text:
                    self.input.add_at_cursor(text)
            last_time = time.time_ns()

    def consumer(self, text):
        pass

    def clear_text(self):
        self.input.set_text('')

    def enter_text(self):
        if self.input.text != '':
            self.state = False

    def cancel(self):
        self.input.set_text('')
        self.state = False


class customVKRenderer(vkb.VKeyboardRenderer):
    """
    A VKeyboardRenderer is in charge of keyboard rendering.

    It handles keyboard rendering properties such as color or padding,
    and provides several rendering methods.

    .. note::
        A DEFAULT and DARK styles are available as class attribute.
    """


    def __init__(self):
        super().__init__(font_name=vkb.VKeyboardRenderer.DARK.font_name,
                         text_color=vkb.VKeyboardRenderer.DARK.text_color,
                         cursor_color=vkb.VKeyboardRenderer.DARK.cursor_color,
                         selection_color=vkb.VKeyboardRenderer.DARK.selection_color,
                         background_color=vkb.VKeyboardRenderer.DARK.background_color,
                         background_key_color=vkb.VKeyboardRenderer.DARK.background_key_color,
                         background_input_color=vkb.VKeyboardRenderer.DARK.background_input_color,
                         text_special_key_color=vkb.VKeyboardRenderer.DARK.text_special_key_color,
                         background_special_key_color=vkb.VKeyboardRenderer.DARK.background_special_key_color
                        )

    def draw_key(self, surface, key):
        """Default drawing method for key.

        Draw the key accordingly to it type.

        Parameters
        ----------
        surface:
            Surface background should be drawn in.
        key:
            Target key to be drawn.
        """
        basename = key.__class__.__bases__[0].__name__
        if isinstance(key, vkeys.VSpaceKey):
            self.draw_space_key(surface, key)
        elif isinstance(key, vkeys.VBackKey):
            self.draw_back_key(surface, key)
        elif isinstance(key, vkeys.VUppercaseKey):
            self.draw_uppercase_key(surface, key)
        elif isinstance(key, vkeys.VSpecialCharKey):
            self.draw_special_char_key(surface, key)
        elif 'VActionKey' in basename:
            self.draw_action_key(surface, key)
        else:
            self.draw_character_key(surface, key)


    def draw_action_key(self, surface, key):
        """Default drawing method for action key.
        Drawn as character key.

        Parameters
        ----------
        surface:
            Surface background should be drawn in.
        key:
            Target key to be drawn.
        """
        self.draw_character_key(surface, key, True)


def keyboard(screen):


    keys = [
            ['1','2','3','4','5','6','7','8','9','0'],
            ['q','w','e','r','t','y','u','i','o','p'],
            ['a','s','d','f','g','h','j','k','l','/'],
            ['z','x','c','v','b','n','m','.','@','_'],
           ]

    cRendererd = customVKRenderer()
    cLayout = customVKLayout(keys)

    keyboard = customVKeyboard(surface = screen,
                                 main_layout = cLayout,
                                 renderer = cRendererd)

    # Main loop
    clock = pygame.time.Clock()

    while keyboard.state:

        clock.tick(100)

        events = pygame.event.get()

        keyboard.update(events)
        rects = keyboard.draw(screen)

        pygame.display.update(rects)

    inputName = keyboard.get_text()
    return inputName

if __name__ == '__main__':
    pygame.init()
    surface = pygame.display.set_mode((800,480))
    name = keyboard(surface)
    print(name)
