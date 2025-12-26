import pygame


class KeyBoardControls:
    def __init__(self) -> None:
        # movement
        self.isLeftPressed = False
        self.isRightPressed = False
        self.isUpPressed = False
        self.isDownPressed = False

        # actions
        self.isFirePressed = False      # SPACE
        self.isMagic1Pressed = False    # J
        self.isMagic2Pressed = False    # K
        self.isMissilePressed = False   # L
        self.isExitPressed = False

        # just-released flags
        self.magic1JustReleased = False
        self.magic2JustReleased = False

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self) -> None:
        # reset release flags each frame
        self.magic1JustReleased = False
        self.magic2JustReleased = False

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.isExitPressed = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.isLeftPressed = True
                elif event.key == pygame.K_d:
                    self.isRightPressed = True
                elif event.key == pygame.K_w:
                    self.isUpPressed = True
                elif event.key == pygame.K_s:
                    self.isDownPressed = True

                elif event.key == pygame.K_SPACE:
                    self.isFirePressed = True
                elif event.key == pygame.K_j:
                    self.isMagic1Pressed = True
                elif event.key == pygame.K_k:
                    self.isMagic2Pressed = True
                elif event.key == pygame.K_l:
                    self.isMissilePressed = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.isLeftPressed = False
                elif event.key == pygame.K_d:
                    self.isRightPressed = False
                elif event.key == pygame.K_w:
                    self.isUpPressed = False
                elif event.key == pygame.K_s:
                    self.isDownPressed = False

                elif event.key == pygame.K_SPACE:
                    self.isFirePressed = False
                elif event.key == pygame.K_j:
                    self.isMagic1Pressed = False
                    self.magic1JustReleased = True
                elif event.key == pygame.K_k:
                    self.isMagic2Pressed = False
                    self.magic2JustReleased = True
                elif event.key == pygame.K_l:
                    self.isMissilePressed = False

    # -------------------------
    # PROPERTIES (READ-ONLY)
    # -------------------------
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

    @property
    def main_weapon_button(self) -> bool:
        return self.isFirePressed

    @property
    def magic_1_button(self) -> bool:
        return self.isMagic1Pressed

    @property
    def magic_2_button(self) -> bool:
        return self.isMagic2Pressed

    @property
    def magic_1_released(self) -> bool:
        return self.magic1JustReleased

    @property
    def magic_2_released(self) -> bool:
        return self.magic2JustReleased

    @property
    def fire_missiles(self) -> bool:
        return self.isMissilePressed
