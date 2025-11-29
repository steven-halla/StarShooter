import pygame
from pygame import surface

from Constants.GlobalConstants import GlobalConstants


class Screen():
    def __init__(self):
        self.height: int = 500
        self.width: int = 500
        self.color: str = GlobalConstants.BLACK

    def start(self, state):
        pass

    def update(self, state):
        pass

    def draw(self,state):
        state.DISPLAY.fill(GlobalConstants.BLACK)
        print("mew")
