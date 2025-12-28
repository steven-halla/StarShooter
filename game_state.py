import pygame
import json

from Constants.GlobalConstants import GlobalConstants
from Entity.StarShip import StarShip
from Levels.LevelTwo import LevelTwo
from Levels.levelThree import LevelThree
from ScreenClasses.MissionBriefingScreenLevelFour import MissionBriefingScreenLevelFour
from ScreenClasses.MissionBriefingScreenLevelOne import MissionBriefingScreenLevelOne
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.Screen import Screen
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen
from Levels.LevelOne import LevelOne

import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.StarShip import StarShip
from Levels.LevelOne import LevelOne
from ScreenClasses.MissionBriefingScreenLevelOne import MissionBriefingScreenLevelOne


class GameState:
    def __init__(self):
        # --------------------------------------------------
        # DISPLAY (WINDOW SIZE ONLY — NEVER GAMEPLAY HEIGHT)
        # --------------------------------------------------
        self.DISPLAY: pygame.Surface = pygame.display.set_mode(
            GlobalConstants.WINDOWS_SIZE
        )

        pygame.display.set_caption("Star Shooter")

        # --------------------------------------------------
        # GAME STATE
        # --------------------------------------------------
        self.isRunning: bool = True

        # --------------------------------------------------
        # GLOBAL PLAYER INSTANCE
        # --------------------------------------------------
        self.starship: StarShip = StarShip()

        # --------------------------------------------------
        # CURRENT SCREEN
        # --------------------------------------------------
        self.currentScreen = MissionBriefingScreenLevelTwo()



