# this file should go to local packages folder

import pygame.draw
import pygame.math
import math
import os


class Event:
    def __init__(self, id, name):
        self.__id = id
        self.__name = name

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    def __repr__(self):
        return f"<Event ID={self.__id} Name={self.__name}>"


class Events:
    CLOSE_APP = Event(0, "Close-App")
    BUTTON_CLICK = Event(1, "Button-Click")
    TOGGLE_VISIBILITY = Event(2, "Toggle-Visible")
    JUST_CLICKED_FRAME = Event(5, "Just-Clicked-Frame")
    MOVING_FRAME = Event(6, "Moving-Frame")

    ALL_EVENTS = {0: CLOSE_APP,
                  1: BUTTON_CLICK,
                  2: TOGGLE_VISIBILITY,
                  5: JUST_CLICKED_FRAME,
                  6: MOVING_FRAME}

    @staticmethod
    def getEventFromID(event_id):
        return Events.ALL_EVENTS[event_id]


class ButtonType:
    VISIBILITY = {"color": (246, 199, 68), "offset": pygame.math.Vector2(30, 15)}
    CLOSE = {"color": (252, 96, 77), "offset": pygame.math.Vector2(15, 15)}

    @staticmethod
    def getButtonFromTypeID(button_id):
        if button_id == 0:
            return ButtonType.VISIBILITY
        elif button_id == 1:
            return ButtonType.CLOSE


class FrameButton:
    RADIUS = 5

    def __init__(self, frame, type):
        self.__frame = frame
        self.__button = type
        self.__pressed = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.__button["color"], self.__frame.getPosition() + self.__button["offset"], FrameButton.RADIUS)

    def update(self, mpos, mbuttons):
        buttonPos: pygame.math.Vector2 = self.__frame.getPosition() + self.__button["offset"]

        distance = math.hypot(mpos[0]-buttonPos.x, mpos[1]-buttonPos.y)

        if not mbuttons[0]:
            self.__pressed = False
        if distance <= FrameButton.RADIUS and mbuttons[0] and not self.__pressed:
            self.__pressed = True
            return Events.BUTTON_CLICK
        return None

    def __repr__(self):
        return f"<FrameButton color={self.__button['color']} pos={self.__frame.pos + self.__button['offset']} frame={self.__frame}>"


class Frame:
    def __init__(self, title, size, pos):
        self.__title = title
        self.__pos = pygame.Vector2(pos)
        self.__window_size = size
        self.__size = (size[0], 30)
        self.__movable_area = pygame.Rect(self.__pos, self.__size)
        self.__movable = True
        self.__pressed = False
        self.__pressed_before = False
        self.__buttons = {"visible": FrameButton(self, ButtonType.VISIBILITY),
                          "close": FrameButton(self, ButtonType.CLOSE)}
        self.__font = pygame.font.SysFont("arial", 15)

    def __render_title(self):
        rendered = self.__font.render(self.__title, True, (255, 255, 255))
        return rendered

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (10, 10, 10), self.__movable_area, border_top_left_radius=10, border_top_right_radius=10)
        for button in self.__buttons.values():
            button.draw(surface)
        title_surface = self.__render_title()
        surface.blit(title_surface, title_surface.get_rect(center=self.__movable_area.center))

    def update(self, mpos, mrel, mbuttons):
        events = []
        button_return = False
        for key, button in self.__buttons.items():
            val = button.update(mpos, mbuttons)
            if val:
                button_return = True
                if key == "visible":
                    events.append(Events.TOGGLE_VISIBILITY)
                elif key == "close":
                    events.append(Events.CLOSE_APP)

        if self.__movable:
            if not mbuttons[0]:
                self.__pressed = False
                self.__pressed_before = False

            if not self.__movable_area.collidepoint(mpos) and mbuttons[0] and not self.__pressed_before:
                self.__pressed_before = True

            if self.__movable_area.collidepoint(mpos) and mbuttons[0] and not self.__pressed and not self.__pressed_before:
                self.__pressed = True
                if not button_return:
                    events.append(Events.JUST_CLICKED_FRAME)
                return events

            if self.__pressed:
                self.setPosition(mrel)
                events.append(Events.MOVING_FRAME)
        else:
            self.__pressed_before = False
            self.__pressed = False
        return events

    def getPosition(self):
        return self.__pos

    def isMovable(self):
        return self.__movable

    def setMovable(self, value):
        self.__movable = value

    def setTitle(self, new_title):
        self.__title = new_title

    def setPosition(self, pos):
        self.__pos.update(self.__pos.x + pos[0], self.__pos.y + pos[1])
        self.__movable_area.update(self.__pos, self.__size)

    def setSize(self, size):
        self.__window_size = size
        self.__size = (size[0], 30)
        self.__movable_area = pygame.Rect(self.__pos, self.__size)

    def getFont(self):
        return self.__font

class Window:
    def __init__(self, **kwargs):
        self.__total_size = kwargs.get("size", (256, 256))
        self.__size = (self.__total_size[0], self.__total_size[1]-30)

        self.__pos = pygame.Vector2(kwargs.get("pos", (0, 0)))
        self.__screen_pos = pygame.Vector2(self.__pos.x, self.__pos.y + 30)
        self.__frame = Frame(kwargs.get("title"), self.__total_size, self.__pos)
        self.__app_surface = pygame.Surface(self.__size)
        self.fill((255, 255, 255))

    def fill(self, color):
        self.__app_surface.fill(color)

    def __get_round_surface(self):
        surf = pygame.Surface(self.__size, pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(surf, (255, 255, 255), ((0, 0), self.__size), border_bottom_right_radius=10,
                         border_bottom_left_radius=10)

        surf.blit(self.__app_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return surf

    def __handle_events(self, events):
        for event in events:
            if event.id == 6:
                self.__pos.update(self.__frame.getPosition())
                self.__screen_pos.update(self.__pos.x, self.__pos.y+30)

    def draw(self, surface):
        self.__frame.draw(surface)
        surface.blit(self.__get_round_surface(), self.__screen_pos)

    def update(self, mpos, mrel, mbuttons):
        events = self.__frame.update(mpos, mrel, mbuttons)
        self.__handle_events(events)
        return events

    def getFrame(self):
        return self.__frame

    def setPos(self, pos):
        self.__frame.setPosition(pos)

        self.__pos.update(self.__frame.getPosition())
        self.__screen_pos.update(self.__pos.x, self.__pos.y + 30)

    def getSurface(self):
        return self.__app_surface

    def getTotalSize(self):
        return self.__total_size

    def getScreenSize(self):
        return self.__size

    def setSize(self, size):
        self.__total_size = size
        self.__size = (self.__total_size[0], self.__total_size[1]-30)

        self.__app_surface = pygame.Surface(self.__size, pygame.SRCALPHA)
        self.__app_surface.fill((255, 255, 255))

        self.__frame.setSize(size)

    def getPosition(self):
        return self.__pos

    def getScreenPos(self):
        return self.__screen_pos

class App:
    def __init__(self, **kwargs):
        self.window = Window(**kwargs)
        self.assets = {}
        self.info = {"author": kwargs.get("author", "Unknown"), "version": kwargs.get("version", "1.0.0")}
        self.__project_path = kwargs.get("project_path")
        self.__asset_path = kwargs.get("assets_path")
        self.renew_assets()

    @property
    def movable(self):
        return self.window.getFrame().isMovable()

    @movable.setter
    def movable(self, val):
        self.window.getFrame().setMovable(val)

    def draw(self, surface):
        self.window.draw(surface)
        self.appDraw(surface)

    def update(self, dt, keys, mpos, mrel, mbuttons):
        events = self.window.update(mpos, mrel, mbuttons)
        self.appUpdate(dt, keys, mpos, mrel, mbuttons)
        return events

    def appDraw(self, surface):
        pass

    def appUpdate(self, dt, keys, mpos, mrel, mbuttons):
        pass

    def renew_assets(self):
        for file in os.listdir(self.__project_path + self.__asset_path):
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpge"):
                self.assets[file.split('.')[0]] = pygame.image.load(self.__project_path+self.__asset_path+file).convert()

    def set_title(self, new_title):
        self.window.getFrame().setTitle(new_title)

    def setPos(self, pos):
        self.window.setPos(pos)

    def setSize(self, size):
        self.window.setSize(size)

    def getAsset(self, name):
        return self.assets[name]
