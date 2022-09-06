import pygame
from foxos import Base


class Button:
    def __init__(self, text, x, y, w, h, color, hover_color, pressed_color):
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.__is_hover = False
        self.__is_pressed = False

    def draw(self, surface, font: pygame.font.Font):
        color = self.color
        if self.__is_hover:
            color = self.hover_color
        if self.__is_pressed:
            color = self.pressed_color

        pygame.draw.rect(surface, color, pygame.Rect(self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(self.x, self.y, self.w, self.h), width=2)
        text = font.render(self.text, True, (0, 0, 0))
        surface.blit(text, text.get_rect(center=(self.x + self.w/2, self.y+self.h/2)))

    def update(self, mpos, mkey, offset):
        if self.x + offset[0] <= mpos[0] <= self.x+self.w + offset[0]+30 and self.y + offset[1] <= mpos[1] <= self.y+self.h + offset[1]+30:
            self.__is_hover = True

            if mkey[0]:
                self.__is_pressed = True
            else:
                self.__is_pressed = False
        else:
            self.__is_hover = False
            self.__is_pressed = False
        return self.__is_pressed

    def isPressed(self):
        return self.__is_pressed

    def isHovering(self):
        return self.__is_hover


class MyEpicGame(Base.App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, title="Paint", size=(512, 512), pos=(0, 0))

        self.button = Button("Reset", self.window.getScreenSize()[0]-64, self.window.getScreenSize()[1]-32, 64, 32, (200, 200, 200), (120, 120, 120), (60, 60, 60))
        self.last_mpos = pygame.mouse.get_pos()
        self.__isPressing = False

    def appDraw(self, surface):
        if self.button.isPressed():
            self.window.fill((255, 255, 255))
        self.button.draw(self.window.getSurface(), self.window.getFrame().getFont())

    def appUpdate(self, dt, keys, mpos, mrel, mbuttons):
        self.button.update(mpos, mbuttons, self.window.getPosition())

        if not mbuttons[0]:
            self.__isPressing = False

        if mbuttons[0] and not self.button.isHovering() and not self.button.isPressed():
            posx = mpos[0] - self.window.getScreenPos()[0] - 2
            posy = mpos[1] - self.window.getScreenPos()[1] - 2
            if self.__isPressing:
                pygame.draw.line(self.window.getSurface(), (255, 0, 0), (posx, posy), self.last_mpos, width=4)
            else:
                pygame.draw.line(self.window.getSurface(), (255, 0, 0), (posx, posy), (posx, posy), width=4)
                self.__isPressing = True
            self.last_mpos = (posx, posy)


def loadApp(**kwargs):
    return MyEpicGame(**kwargs)
