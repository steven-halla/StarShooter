import pygame
from Constants.GlobalConstants import GlobalConstants
from Controller.KeyBoardControls import KeyBoardControls
from Entity.StarShip import StarShip
from Movement.MoveRectangle import MoveRectangle


class VerticalBattleScreen:
    def __init__(self):
        self.starship: StarShip = StarShip()
        self.isStart: bool = True
        self.mover: MoveRectangle = MoveRectangle()
        self.controller: KeyBoardControls = KeyBoardControls()

    def start(self, state):
        # Center X in the window, place near bottom
        self.starship.x = GlobalConstants.WINDOWS_SIZE[0] // 2
        self.starship.y = GlobalConstants.WINDOWS_SIZE[1] - 100

    def update(self, state):  # ✅ removed ", controller"
        if self.isStart:
            self.start(state)
            self.isStart = False

        # update keyboard state
        self.controller.update()

        # move once per press using the controller's edge-triggered property
        if self.controller.left_button:
            self.mover.move_left(self.starship)

    def draw(self, state):
        state.DISPLAY.fill(GlobalConstants.BLACK)
        self.starship.draw(state.DISPLAY)
        pygame.display.flip()
