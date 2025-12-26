import pygame


class KeyBoardControls:
    def __init__(self) -> None:
        self.isLeftPressed: bool = False
        self.isRightPressed: bool = False
        self.isUpPressed: bool = False
        self.isDownPressed: bool = False
        self.isExitPressed: bool = False
        self.isFPressed: bool = False
        self.isQPressed: bool = False
        self.isAPressed: bool = False
        self.isDPressed: bool = False
        self.isSPressed: bool = False
        self.isWPressed: bool = False
        self.dJustReleased = False
        self.sJustReleased = False

    @property
    def magic_1_released(self):
        return self.dJustReleased

    @property
    def magic_2_released(self):
        return self.sJustReleased



    def update(self):
        # reset flags at the start of each frame
        self.dJustReleased = False
        self.sJustReleased = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isExitPressed = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.isLeftPressed = True
                elif event.key == pygame.K_RIGHT:
                    self.isRightPressed = True
                elif event.key == pygame.K_UP:
                    self.isUpPressed = True
                elif event.key == pygame.K_DOWN:
                    self.isDownPressed = True
                elif event.key == pygame.K_f:
                    self.isFPressed = True
                elif event.key == pygame.K_q:
                    self.isQPressed = True
                elif event.key == pygame.K_a:
                    self.isAPressed = True
                elif event.key == pygame.K_d:
                    self.isDPressed = True
                elif event.key == pygame.K_s:
                    self.isSPressed = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.isLeftPressed = False
                elif event.key == pygame.K_RIGHT:
                    self.isRightPressed = False
                elif event.key == pygame.K_UP:
                    self.isUpPressed = False
                elif event.key == pygame.K_DOWN:
                    self.isDownPressed = False
                elif event.key == pygame.K_f:
                    self.isFPressed = False
                elif event.key == pygame.K_q:
                    self.isQPressed = False
                elif event.key == pygame.K_a:
                    self.isAPressed = False
                elif event.key == pygame.K_d:
                    # D released: clear pressed state and set the "just released" flag
                    self.isDPressed = False
                    self.dJustReleased = True
                elif event.key == pygame.K_s:
                    # S released: clear pressed state and set the "just released" flag
                    self.isSPressed = False
                    self.sJustReleased = True

    @property
    def left_button(self) -> bool:
        return self.isAPressed

    @property
    def right_button(self) -> bool:
        return self.isDPressed

    @property
    def up_button(self) -> bool:
        return self.isWPressed

    @property
    def down_button(self) -> bool:

        return self.isDownPressed

    @property
    def main_weapon_button(self) -> bool:
        return self.isFPressed


    @property
    def fire_missiles(self) -> bool:
        return self.isAPressed

    @property
    def magic_1_button(self) -> bool:
        return self.isDPressed

    @property
    def magic_2_button(self) -> bool:
        return self.isSPressed

    @property
    def q_button(self) -> bool:
        return self.isQPressed

    @property
    def a_button(self) -> bool:
        return self.isAPressed

    @property
    def d_button(self) -> bool:
        return self.isDPressed

    @property
    def s_button(self) -> bool:
        return self.isSPressed
