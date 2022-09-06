import importlib
import json
import os
import time

import pygame

APPS_PATH = "./apps"


class AppManager:
    APPS = {}
    WORKING_APPS = []
    HIDDEN_APPS = []

    @staticmethod
    def prepareApp(name):
        appDataFile = APPS_PATH + "/" + name + "/app-data.json"
        if os.path.exists(appDataFile):
            with open(appDataFile, "r", encoding="utf-8") as f:
                appData = json.loads(f.read())

            mainFileName = appData["main-file"]

            pathToMainFile = APPS_PATH[2:] + "." + name + "." + mainFileName[:-3].replace("/", ".")

            namespace = importlib.__import__(name=pathToMainFile)

            loadFunction = namespace
            for part in pathToMainFile.split(".")[1:]:
                loadFunction = getattr(loadFunction, part)
            loadFunction = getattr(loadFunction, "loadApp")

            AppManager.APPS[name] = [loadFunction, [appData, APPS_PATH + "/" + name + "/"]]

    @staticmethod
    def runApp(name):
        data = AppManager.APPS[name][1]

        app = AppManager.APPS[name][0](author=data[0]["author"], version=data[0]["version"],
                                       assets_path=data[0]["assets-folder"], project_path=data[1])

        AppManager.WORKING_APPS.append(app)

    @staticmethod
    def hideApp(app):
        AppManager.WORKING_APPS.remove(app)
        AppManager.HIDDEN_APPS.append(app)

    @staticmethod
    def showApp(app):
        AppManager.WORKING_APPS.append(app)
        AppManager.HIDDEN_APPS.remove(app)

    @staticmethod
    def killApp(app):
        if app in AppManager.WORKING_APPS:
            AppManager.WORKING_APPS.remove(app)
        if app in AppManager.HIDDEN_APPS:
            AppManager.HIDDEN_APPS.remove(app)

    @staticmethod
    def getShortcut(name, resize=(62, 56)):
        data = AppManager.APPS[name][1]

        icon = pygame.transform.scale(
            pygame.image.load(data[1] + data[0]["assets-folder"] + data[0]["shortcut-icon-name"]), resize)

        return {"name": name, "shortcut-name": data[0]["shortcut-name"], "shortcut-icon": icon}


class Shortcut:
    FONT = pygame.font.Font("./fonts/SEGOEUI.TTF", 10)

    def __init__(self, name, shortcut_name, shortcut_icon):
        self.__name = name
        self.shortcut_name = shortcut_name
        self.shortcut_icon = shortcut_icon
        self.selected = False

    def runApp(self):
        AppManager.runApp(self.__name)

    def renderAt(self, surface: pygame.Surface, x, y):
        textRender = Shortcut.FONT.render(self.shortcut_name, True, (255, 255, 255))
        if self.selected:
            pygame.draw.rect(surface, (0, 0, 255), pygame.Rect(x, y + 56, 64, 8))

        surface.blit(self.shortcut_icon, (x + 1, y))
        surface.blit(textRender, textRender.get_rect(center=(x + 32, y + 60)))


class ShortcutManager:
    def __init__(self, screen_size):
        self.grid = [[None] * (screen_size[1] // 64) for _ in range(screen_size[0] // 64)]
        self.last_click = 0
        self.__pressed = False
        self.last_click_shortcut = None

    def loadShortcuts(self):
        idx = 0
        for name in AppManager.APPS.keys():
            data = AppManager.getShortcut(name)
            self.grid[idx % len(self.grid)][idx // len(self.grid[0])] = Shortcut(*data.values())
            idx += 1

    def draw(self, surface):
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if self.grid[x][y] is not None:
                    self.grid[x][y].renderAt(surface, x * 64, y * 64)

    def update(self):
        mpos = pygame.mouse.get_pos()
        keys = pygame.mouse.get_pressed(3)

        if not keys[0]:
            self.__pressed = False

        gridX, gridY = mpos[0] // 64, mpos[1] // 64

        if self.grid[gridX][gridY] is None and keys[0]:
            self.__pressed = True
            if self.last_click_shortcut:
                self.last_click_shortcut.selected = False

        if not self.__pressed and self.grid[gridX][gridY] is not None and keys[0]:
            if time.time() - self.last_click <= 0.2 and self.last_click_shortcut == self.grid[gridX][gridY]:
                self.last_click_shortcut.runApp()
            elif self.last_click_shortcut is not None and self.last_click_shortcut != self.grid[gridX][gridY]:
                self.last_click_shortcut.selected = False

            self.last_click = time.time()
            self.last_click_shortcut = self.grid[gridX][gridY]
            self.last_click_shortcut.selected = True

            self.__pressed = True


class Background:
    def __init__(self, image):
        self.image = image

    def render(self, surface: pygame.Surface):
        surface.blit(pygame.transform.scale(self.image, surface.get_size()), (0, 0))
