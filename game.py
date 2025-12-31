import pygame
import logging

from Constants.GlobalConstants import GlobalConstants
from game_state import GameState

# logging.basicConfig(
#     level=logging.INFO,  # INFO
#     format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
# )

# Instantiate mixer
# this is where we get our music:
# https://soundimage.org/chiptunes-2/

class Game:
    def __init__(self):
        # global logging
        pygame.init()
        pygame.display.set_caption("Star Shooter")
        self.state = GameState()  # create a new GameState()

    def start(self):
        clock = pygame.time.Clock()

        # 🔴 REQUIRED — initialize the first screen
        self.state.currentScreen.start(self.state)

        while self.state.isRunning:
            self.state.delta = clock.tick(GlobalConstants.FPS)

            self.state.currentScreen.update(self.state)
            self.state.currentScreen.draw(self.state)

        pygame.quit()

# Welcome to Casino Hell! May the odds be ever in your favor... or not. The house always wins!
