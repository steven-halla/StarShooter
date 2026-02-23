import pygame


class KeyBoardControls:
    def __init__(self) -> None:
        self.isBPressedSwitch: bool = False
        self.isYPressedSwitch: bool = False
        self.isAPressedSwitch: bool = False
        self.isXPressedSwitch: bool = False
        self.isStartPressedSwitch: bool = False
        self.isExitPressed: bool = False
        self.isLeftPressedSwitch: bool = False
        self.isRightPressedSwitch: bool = False
        self.isUpPressedSwitch: bool = False
        self.isDownPressedSwitch: bool = False
        self.isFPressed: bool = False
        self.isQPressed: bool = False
        self.isDPressed: bool = False
        self.isSPressed: bool = False
        self.dJustReleased = False
        self.sJustReleased = False
        self.bJustReleased = False
        self.yJustReleased = False

        self._last_b_state: bool = False
        self._last_y_state: bool = False

        # Joystick initialization
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None

    @property
    def magic_1_released(self):
        return self.dJustReleased or self.bJustReleased or self.yJustReleased

    @property
    def magic_2_released(self):
        return self.sJustReleased



    def update(self):
        # reset flags at the start of each frame
        self.dJustReleased = False
        self.sJustReleased = False
        self.bJustReleased = False
        self.yJustReleased = False

        keys = pygame.key.get_pressed()
        self.isLeftPressedSwitch = keys[pygame.K_LEFT]
        self.isRightPressedSwitch = keys[pygame.K_RIGHT]
        self.isUpPressedSwitch = keys[pygame.K_UP]
        self.isDownPressedSwitch = keys[pygame.K_DOWN]
        self.isFPressed = keys[pygame.K_f]
        self.isBPressedSwitch = keys[pygame.K_b]
        self.isYPressedSwitch = keys[pygame.K_y]
        self.isAPressedSwitch = keys[pygame.K_a]
        self.isDPressed = keys[pygame.K_d]
        self.isSPressed = keys[pygame.K_s]
        self.isQPressed = keys[pygame.K_q]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isExitPressed = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    # D released: clear pressed state and set the "just released" flag
                    self.dJustReleased = True
                elif event.key == pygame.K_s:
                    # S released: clear pressed state and set the "just released" flag
                    self.sJustReleased = True

            # Handle D-pad input (JOYHATMOTION)
            elif event.type == pygame.JOYHATMOTION and self.joystick:
                if event.hat == 0:  # Assuming the D-pad is the first hat
                    hat_x, hat_y = event.value
                    self.isLeftPressedSwitch = (hat_x == -1)
                    self.isRightPressedSwitch = (hat_x == 1)
                    self.isUpPressedSwitch = (hat_y == 1)
                    self.isDownPressedSwitch = (hat_y == -1)

            # Handle button input (JOYBUTTONDOWN and JOYBUTTONUP)
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A button
                    self.isAPressedSwitch = True
                elif event.button == 1:  # B button
                    self.isBPressedSwitch = True
                elif event.button == 2:  # X button
                    self.isXPressedSwitch = True
                elif event.button == 3:  # Y button
                    self.isYPressedSwitch = True
                elif event.button == 6:  # Start
                    self.isStartPressedSwitch = True
                elif event.button == 11:  # D-pad Up
                    self.isUpPressedSwitch = True
                elif event.button == 12:  # D-pad Down
                    self.isDownPressedSwitch = True
                elif event.button == 13:  # D-pad Left
                    self.isLeftPressedSwitch = True
                elif event.button == 14:  # D-pad Right
                    self.isRightPressedSwitch = True

            elif event.type == pygame.JOYBUTTONUP:
                if event.button == 0:  # A button
                    self.isAPressedSwitch = False
                elif event.button == 1:  # B button
                    self.isBPressedSwitch = False
                    self.bJustReleased = True
                elif event.button == 2:  # X button
                    self.isXPressedSwitch = False
                elif event.button == 3:  # Y button
                    self.isYPressedSwitch = False
                    self.yJustReleased = True
                elif event.button == 6:  # Start
                    self.isStartPressedSwitch = False
                elif event.button == 11:  # D-pad Up
                    self.isUpPressedSwitch = False
                elif event.button == 12:  # D-pad Down
                    self.isDownPressedSwitch = False
                elif event.button == 13:  # D-pad Left
                    self.isLeftPressedSwitch = False
                elif event.button == 14:  # D-pad Right
                    self.isRightPressedSwitch = False

    @property
    def left_button(self) -> bool:
        return self.isLeftPressedSwitch

    @property
    def right_button(self) -> bool:
        return self.isRightPressedSwitch

    @property
    def up_button(self) -> bool:
        return self.isUpPressedSwitch

    @property
    def down_button(self) -> bool:

        return self.isDownPressedSwitch

    @property
    def main_weapon_button(self) -> bool:
        return self.isAPressedSwitch or self.isFPressed


    @property
    def fire_missiles(self) -> bool:
        return self.isBPressedSwitch or self.isYPressedSwitch

    @property
    def magic_1_button(self) -> bool:
        return self.isXPressedSwitch or self.isDPressed

    @property
    def magic_2_button(self) -> bool:
        return self.isSPressed

    @property
    def start_button(self) -> bool:
        if self.isStartPressedSwitch:
            self.isStartPressedSwitch = False
            return True
        return False

    @property
    def q_button(self) -> bool:
        return self.isQPressed

    @property
    def a_button(self) -> bool:
        return self.isAPressedSwitch

    @property
    def d_button(self) -> bool:
        return self.isDPressed

    @property
    def s_button(self) -> bool:
        return self.isSPressed
