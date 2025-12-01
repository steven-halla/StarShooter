import pygame
import json

from Constants.GlobalConstants import GlobalConstants
from ScreenClasses.Screen import Screen
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen
from Levels.LevelOne import LevelOne


class GameState:
    def __init__(self):
        pygame.display.set_mode(GlobalConstants.WINDOWS_SIZE)  # or GlobalConstants.WINDOWS_SIZE if you prefer

        self.currentScreen = LevelOne()
        self.isRunning: bool = True
        self.DISPLAY: pygame.Surface = pygame.display.set_mode(GlobalConstants.WINDOWS_SIZE)



