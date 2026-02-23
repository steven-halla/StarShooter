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
        self.isDPressed: bool = False
        self.isSPressed: bool = False

        self.dJustReleased: bool = False
        self.sJustReleased: bool = False
        self.bJustReleased: bool = False
        self.yJustReleased: bool = False

        self._last_b_state: bool = False
        self._last_y_state: bool = False

        self.isQPressed: bool = False
        self.qJustPressed: bool = False

        # joystick
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None

        self.debug_input: bool = False
        self._last_hat = None
        self._last_axis = None
        self._last_dpad_buttons = None

    @property
    def magic_1_released(self) -> bool:
        return self.dJustReleased or self.bJustReleased or self.yJustReleased

    @property
    def magic_2_released(self) -> bool:
        return self.sJustReleased

    def update(self):
        # reset one-frame flags
        self.dJustReleased = False
        self.sJustReleased = False
        self.bJustReleased = False
        self.yJustReleased = False
        self.qJustPressed = False

        # let pygame update internal joystick state BEFORE polling
        pygame.event.pump()

        # -------------------------
        # KEYBOARD (held state)
        # -------------------------
        keys = pygame.key.get_pressed()
        kb_left = bool(keys[pygame.K_LEFT])
        kb_right = bool(keys[pygame.K_RIGHT])
        kb_up = bool(keys[pygame.K_UP])
        kb_down = bool(keys[pygame.K_DOWN])

        self.isFPressed = bool(keys[pygame.K_f])
        kb_b = bool(keys[pygame.K_b])
        kb_y = bool(keys[pygame.K_y])
        kb_a = bool(keys[pygame.K_a])
        self.isDPressed = bool(keys[pygame.K_d])
        self.isSPressed = bool(keys[pygame.K_s])

        # Q "just pressed"
        if keys[pygame.K_q]:
            if not self.isQPressed:
                self.qJustPressed = True
                if self.debug_input:
                    print("[INPUT] Q JUST PRESSED")
            self.isQPressed = True
        else:
            self.isQPressed = False

        # Start from keyboard state (controller will OR in below)
        self.isLeftPressedSwitch = kb_left
        self.isRightPressedSwitch = kb_right
        self.isUpPressedSwitch = kb_up
        self.isDownPressedSwitch = kb_down

        self.isBPressedSwitch = kb_b
        self.isYPressedSwitch = kb_y
        self.isAPressedSwitch = kb_a

        # -------------------------
        # EVENTS (release flags + quit)
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isExitPressed = True
                if self.debug_input:
                    print("[INPUT] QUIT")

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.dJustReleased = True
                    if self.debug_input:
                        print("[INPUT] D JUST RELEASED")
                elif event.key == pygame.K_s:
                    self.sJustReleased = True
                    if self.debug_input:
                        print("[INPUT] S JUST RELEASED")

        # -------------------------
        # JOYSTICK POLLING (held state every frame)
        # -------------------------
        if self.joystick is not None:
            # buttons (held)
            a_held = bool(self.joystick.get_button(0))
            b_held = bool(self.joystick.get_button(1))
            x_held = bool(self.joystick.get_button(2))
            y_held = bool(self.joystick.get_button(3))
            start_held = bool(self.joystick.get_button(6))

            self.isAPressedSwitch = self.isAPressedSwitch or a_held
            self.isBPressedSwitch = self.isBPressedSwitch or b_held
            self.isXPressedSwitch = x_held
            self.isYPressedSwitch = self.isYPressedSwitch or y_held
            self.isStartPressedSwitch = start_held

            # Check for B/Y releases (Missile button/Back)
            if self._last_b_state and not b_held:
                self.bJustReleased = True
            if self._last_y_state and not y_held:
                self.yJustReleased = True

            self._last_b_state = b_held
            self._last_y_state = y_held

            # --- D-PAD SOURCE #1: HAT ---
            hat_left = hat_right = hat_up = hat_down = False
            hat_val = None
            if self.joystick.get_numhats() > 0:
                hat_x, hat_y = self.joystick.get_hat(0)
                hat_val = (hat_x, hat_y)
                hat_left = (hat_x == -1)
                hat_right = (hat_x == 1)
                hat_up = (hat_y == 1)
                hat_down = (hat_y == -1)

            # --- D-PAD SOURCE #2: BUTTONS 11-14 (common on mac) ---
            # (you already used these in Casino Hell)
            btn_up = bool(self.joystick.get_button(11))
            btn_down = bool(self.joystick.get_button(12))
            btn_left = bool(self.joystick.get_button(13))
            btn_right = bool(self.joystick.get_button(14))

            # --- D-PAD SOURCE #3: LEFT STICK AXES fallback ---
            axis_left = axis_right = axis_up = axis_down = False
            axis_val = None
            if self.joystick.get_numaxes() >= 2:
                ax0 = self.joystick.get_axis(0)
                ax1 = self.joystick.get_axis(1)
                axis_val = (round(ax0, 2), round(ax1, 2))
                dead = 0.35
                axis_left = ax0 < -dead
                axis_right = ax0 > dead
                axis_up = ax1 < -dead
                axis_down = ax1 > dead

            # combine all dpad sources
            self.isLeftPressedSwitch = self.isLeftPressedSwitch or hat_left or btn_left or axis_left
            self.isRightPressedSwitch = self.isRightPressedSwitch or hat_right or btn_right or axis_right
            self.isUpPressedSwitch = self.isUpPressedSwitch or hat_up or btn_up or axis_up
            self.isDownPressedSwitch = self.isDownPressedSwitch or hat_down or btn_down or axis_down

            # DEBUG raw dpad sources (prints only on change)
            if self.debug_input:
                if hat_val != self._last_hat:
                    print(f"[JOY] hats={self.joystick.get_numhats()} hat0={hat_val}")
                    self._last_hat = hat_val

                dpad_buttons = (btn_left, btn_right, btn_up, btn_down)
                if dpad_buttons != self._last_dpad_buttons:
                    print(f"[JOY] dpad_buttons L/R/U/D = {dpad_buttons} (buttons 13/14/11/12)")
                    self._last_dpad_buttons = dpad_buttons

                if axis_val != self._last_axis:
                    print(f"[JOY] axes0/1={axis_val}")
                    self._last_axis = axis_val

        # -------------------------
        # DEBUG (active state)
        # -------------------------
        if self.debug_input and any([
            self.isLeftPressedSwitch, self.isRightPressedSwitch, self.isUpPressedSwitch, self.isDownPressedSwitch,
            self.isFPressed, self.isBPressedSwitch, self.isYPressedSwitch, self.isAPressedSwitch,
            self.isDPressed, self.isSPressed, self.qJustPressed, self.isXPressedSwitch, self.isStartPressedSwitch
        ]):
            print(
                "[STATE] "
                f"L={self.isLeftPressedSwitch} R={self.isRightPressedSwitch} "
                f"U={self.isUpPressedSwitch} Dn={self.isDownPressedSwitch} "
                f"A={self.isAPressedSwitch} B={self.isBPressedSwitch} X={self.isXPressedSwitch} Y={self.isYPressedSwitch} "
                f"Start={self.isStartPressedSwitch} "
                f"F={self.isFPressed} Dkey={self.isDPressed} Skey={self.isSPressed}"
            )

    # -------------------------
    # PROPERTIES (held state)
    # -------------------------
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
    def start_button(self) -> bool:
        return self.isStartPressedSwitch

    @property
    def magic_2_button(self) -> bool:
        return self.isSPressed

    @property
    def q_just_pressed_button(self) -> bool:
        return self.qJustPressed

    @property
    def a_button(self) -> bool:
        return self.isAPressedSwitch

    @property
    def d_button(self) -> bool:
        return self.isDPressed

    @property
    def s_button(self) -> bool:
        return self.isSPressed

    @property
    def magic_1_released(self) -> bool:
        return self.dJustReleased or self.bJustReleased or self.yJustReleased

    @property
    def magic_2_released(self) -> bool:
        return self.sJustReleased
