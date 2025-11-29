import pygame
import json

from Constants.GlobalConstants import GlobalConstants
from ScreenClasses.Screen import Screen
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class GameState:
    def __init__(self):

        self.currentScreen = VerticalBattleScreen()
        self.isRunning: bool = True
        self.DISPLAY: pygame.Surface = pygame.display.set_mode(GlobalConstants.WINDOWS_SIZE)


