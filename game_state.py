import pygame
import json

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Entity.StarShip import StarShip
from Levels.LevelFive import LevelFive
from Levels.LevelFour import LevelFour
from Levels.LevelSix import LevelSix
from Levels.LevelSeven import LevelSeven
from Levels.LevelTwo import LevelTwo
from Levels.MapTester import MapTester
from Levels.levelThree import LevelThree
from ScreenClasses.MissionBriefingScreenLevelFour import MissionBriefingScreenLevelFour
from ScreenClasses.MissionBriefingScreenLevelOne import MissionBriefingScreenLevelOne
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.Screen import Screen
from ScreenClasses.TextBox import TextBox
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen
from Levels.LevelOne import LevelOne

import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.StarShip import StarShip
from Levels.LevelOne import LevelOne
from ScreenClasses.MissionBriefingScreenLevelOne import MissionBriefingScreenLevelOne
from Weapons.Bullet import Bullet


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
        # Text box to make it global
        # --------------------------------------------------
        self.textbox = TextBox(
            GlobalConstants.BASE_WINDOW_WIDTH,
            GlobalConstants.BASE_WINDOW_HEIGHT
        )

        # --------------------------------------------------
        # GAME STATE
        # --------------------------------------------------
        self.isRunning: bool = True

        # --------------------------------------------------
        # GLOBAL PLAYER INSTANCE
        # --------------------------------------------------
        self.starship: StarShip = StarShip()


        # --------------------------------------------------
        # enemies global
        # --------------------------------------------------
        # self.enemy_list: list[Enemy]

        # --------------------------------------------------
        # CURRENT SCREEN
        # --------------------------------------------------
        self.currentScreen = LevelThree(self.textbox)

        # --------------------------------------------------
        # Bullet list
        # --------------------------------------------------
        # bullets TO DO



