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
        self.STARSHIP_HORIZONTAL_CENTER_DIVISOR: int = 2
        self.STARSHIP_BOTTOM_OFFSET: int = 100
        self.MIN_X: int = 0
        self.MIN_Y: int = 0

    def start(self, state):
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        self.starship.x = window_width // self.STARSHIP_HORIZONTAL_CENTER_DIVISOR
        self.starship.y = window_height - self.STARSHIP_BOTTOM_OFFSET


    def _clamp_starship_to_screen(self) -> None:
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        max_x: int = window_width - self.starship.width
        max_y: int = window_height - self.starship.height

        # clamp X
        if self.starship.x < self.MIN_X:
            self.starship.x = self.MIN_X
        elif self.starship.x > max_x:
            self.starship.x = max_x

        # clamp Y
        if self.starship.y < self.MIN_Y:
            self.starship.y = self.MIN_Y
        elif self.starship.y > max_y:
            self.starship.y = max_y

    def update(self, state):
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        if self.starship.x > window_width:
            self.starship.x = 0
        if self.isStart:
            self.start(state)
            self.isStart = False

        # update keyboard input
        self.controller.update()

        # record old position BEFORE moving
        # old_x = self.starship.x
        # old_y = self.starship.y

        # handle movement
        if self.controller.left_button:
            self.mover.player_move_left(self.starship)
        if self.controller.right_button:
            self.mover.player_move_right(self.starship)
        if self.controller.up_button:
            self.mover.player_move_up(self.starship)
        if self.controller.down_button:
            self.mover.player_move_down(self.starship)

        # # measure frame distance (shows acceleration when diagonal)
        # dx = self.starship.x - old_x
        # dy = self.starship.y - old_y
        # frame_distance = (dx ** 2 + dy ** 2) ** 0.5
        # print(f"x={self.starship.x}, y={self.starship.y}, dx={dx}, dy={dy}, frame_distance={frame_distance}")
        self._clamp_starship_to_screen()

    def draw(self, state):
        state.DISPLAY.fill(GlobalConstants.BLACK)
        self.starship.draw(state.DISPLAY)
        pygame.display.flip()
