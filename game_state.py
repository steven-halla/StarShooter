import pygame
import json

from Constants.GlobalConstants import GlobalConstants
from ScreenClasses.Screen import Screen


class GameState:
    def __init__(self):

        self.currentScreen = Screen()
        self.isRunning: bool = True
        self.DISPLAY: pygame.Surface = pygame.display.set_mode(GlobalConstants.WINDOWS_SIZE)


