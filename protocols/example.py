from touchscreen_protocol import BaseProtocol, Protocol, POINTERPRESSED, POINTERMOTION, POINTERRELEASED
import touchscreen_protocol as ts

class test_1(BaseProtocol):
    def init(self):
        print('Base')

    def main(self):
        import pygame
        #print('Base Main')
        running = True
        self.surface.fill((0,0,0))
        obj1 = pygame.draw.rect(self.surface, (255,0,0), (500,200, 100,100))
        pygame.display.flip()
        while running:
            for event in pygame.event.get():
                position = 0
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]:
                    position = event.pos
                elif event.type in [pygame.FINGERDOWN, pygame.FINGERMOTION,pygame.FINGERUP]:
                    position = (int(event.x*800),int(event.y*480))
                if position:
                    if obj1.collidepoint(position):
                        running = False


class test_2(Protocol):
    def init(self):
        print('prot AAA')

    def main(self,event):
        #print('prot main')
        print(event)

white = (255,255,255)
class testingTouch(Protocol):
    def init(self):
        self.sensor.setHandler(self.sensorHandler)
        self.valve.setOpenTime(.01)
        self.pressed = False
        self.lastposition = 0

    def main(self,event):
        self.log(event)
        self.screen_clean()
        if self.pressed:
            self.draw_circle(white, self.lastposition, 20)
        self.screen_update()

        if event.type == POINTERPRESSED:
            self.pressed = True
            self.draw_circle(white, event.position, 20)
            self.lastposition = event.position
            self.screen_update()
            self.valve.drop()
            self.log('pointer down')
            self.sound.play(frec=440,duration=.2)

        elif event.type == POINTERMOTION:
            self.lastposition = event.position
            self.log('pointer moving')

        elif event.type == POINTERRELEASED:
            self.pressed = False
            self.lastposition = 0
            self.log('pointer released')

    def sensorHandler(self):
        self.log('Decide what to do when the IRbeam was broken')
