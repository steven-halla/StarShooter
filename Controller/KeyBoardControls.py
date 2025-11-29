import pygame


class KeyBoardControls:
    def __init__(self) -> None:
        self.isLeftPressed: bool = False
        self.isRightPressed: bool = False
        self.isUpPressed: bool = False
        self.isDownPressed: bool = False
        self.isExitPressed: bool = False

    def update(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isExitPressed = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.isLeftPressed = True
                elif event.key == pygame.K_RIGHT:
                    self.isRightPressed = True
                elif event.key == pygame.K_UP:
                    self.isUpPressed = True
                elif event.key == pygame.K_DOWN:
                    self.isDownPressed = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.isLeftPressed = False
                elif event.key == pygame.K_RIGHT:
                    self.isRightPressed = False
                elif event.key == pygame.K_UP:
                    self.isUpPressed = False
                elif event.key == pygame.K_DOWN:
                    self.isDownPressed = False

    @property
    def left_button(self) -> bool:
        return self.isLeftPressed

    @property
    def right_button(self) -> bool:
        return self.isRightPressed

    @property
    def up_button(self) -> bool:
        return self.isUpPressed

    @property
    def down_button(self) -> bool:
        return self.isDownPressed
