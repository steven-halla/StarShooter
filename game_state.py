import pygame
import json

from Constants.GlobalConstants import GlobalConstants
from Entity.StarShip import StarShip
from Levels.LevelTwo import LevelTwo
from Levels.levelThree import LevelThree
from ScreenClasses.Screen import Screen
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen
from Levels.LevelOne import LevelOne


class GameState:
    def __init__(self):
        pygame.display.set_mode(GlobalConstants.WINDOWS_SIZE)  # or GlobalConstants.WINDOWS_SIZE if you prefer

        self.currentScreen = LevelTwo()
        self.isRunning: bool = True
        self.starship = StarShip()  # ⭐ GLOBAL SHIP INSTANCE
        self.currentScreen.set_player(self.starship)
        self.DISPLAY: pygame.Surface = pygame.display.set_mode(GlobalConstants.WINDOWS_SIZE)



