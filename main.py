import os

import pygame
import time

pygame.init()

from Components import AppManager, ShortcutManager, Background

DISPLAY = pygame.display.set_mode((64*20, 64*20*0.5))
pygame.display.set_caption("Epic Fox os")


def prepareApps():
    for folder in os.listdir("apps"):
        AppManager.prepareApp(folder)


def mainLoop():
    prepareApps()
    shortcutManager = ShortcutManager(DISPLAY.get_size())
    shortcutManager.loadShortcuts()

    background = Background(pygame.image.load("assets/Debinyan_Wallpaper.png"))

    OS_RUNNING = True

    prev = time.time()
    dt = 0
    while OS_RUNNING:
        now = time.time()
        dt = time.time() - prev
        prev = now

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                OS_RUNNING = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                OS_RUNNING = False

        keys, mpos, mrel, mbuttons = pygame.key.get_pressed(), pygame.mouse.get_pos(), pygame.mouse.get_rel(), pygame.mouse.get_pressed(3)
        # Update
        shortcutManager.update()
        for app in AppManager.WORKING_APPS:
            events = app.update(dt, keys, mpos, mrel, mbuttons)
            if any(event.id == 0 for event in events):
                AppManager.killApp(app)
            elif any(event.id == 2 for event in events):
                AppManager.hideApp(app)
        # Draw
        DISPLAY.fill((0, 0, 0))
        background.render(DISPLAY)
        shortcutManager.draw(DISPLAY)
        for app in AppManager.WORKING_APPS:
            app.draw(DISPLAY)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    mainLoop()