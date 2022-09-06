import pygame
from foxos import Base


class MyEpicGame(Base.App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, title="Epic Epic Game", size=(256, 256), pos=(0, 0))

        self.pos = pygame.Vector2(0, 0)
        self.scale = pygame.Vector2(32, 32)

    def appDraw(self, surface):
        self.window.getSurface().fill((255, 255, 255))
        image: pygame.Surface = self.getAsset("icon")
        self.window.getSurface().blit(pygame.transform.scale(image, self.scale), self.pos)

    def appUpdate(self, dt, keys, mpos, mrel, mbuttons):
        if keys[pygame.K_d]:
            self.pos.x += dt * 50
        if keys[pygame.K_a]:
            self.pos.x -= dt * 50
        if keys[pygame.K_w]:
            self.pos.y -= dt * 50
        if keys[pygame.K_s]:
            self.pos.y += dt * 50

        if keys[pygame.K_SPACE]:
            self.scale += (20*dt, 20*dt)


def loadApp(**kwargs):
    return MyEpicGame(**kwargs)
