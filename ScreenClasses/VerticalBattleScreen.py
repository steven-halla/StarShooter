import pygame
from pygame import Surface

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Controller.KeyBoardControls import KeyBoardControls
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.StarShip import StarShip
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


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

        self.bile_spitter: BileSpitter = BileSpitter()
        self.ENEMY_HORIZONTAL_CENTER_DIVISOR: int = 2
        self.ENEMY_TOP_OFFSET: int = 50

        self.player_bullets: list = []
        self.enemy_bullets: list = []   # Bullet objects ONLY

        self.BULLET_FIRE_INTERVAL_SECONDS: float = 1.0
        self.bullet_timer: Timer = Timer(self.BULLET_FIRE_INTERVAL_SECONDS)

    def start(self, state):
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        self.starship.x = window_width // self.STARSHIP_HORIZONTAL_CENTER_DIVISOR
        self.starship.y = window_height - self.STARSHIP_BOTTOM_OFFSET

        self.bile_spitter.x = window_width // self.ENEMY_HORIZONTAL_CENTER_DIVISOR
        self.bile_spitter.y = self.ENEMY_TOP_OFFSET

    def _clamp_starship_to_screen(self) -> None:
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        max_x = window_width - self.starship.width
        max_y = window_height - self.starship.height

        if self.starship.x < self.MIN_X:
            self.starship.x = self.MIN_X
        elif self.starship.x > max_x:
            self.starship.x = max_x

        if self.starship.y < self.MIN_Y:
            self.starship.y = self.MIN_Y
        elif self.starship.y > max_y:
            self.starship.y = max_y

    def update(self, state):
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        if self.isStart:
            self.start(state)
            self.isStart = False

        self.controller.update()

        if self.controller.left_button:
            self.mover.player_move_left(self.starship)
        if self.controller.right_button:
            self.mover.player_move_right(self.starship)
        if self.controller.up_button:
            self.mover.player_move_up(self.starship)
        if self.controller.down_button:
            self.mover.player_move_down(self.starship)

        self._clamp_starship_to_screen()

        # -------------------------
        # PLAYER BULLET LOGIC (UNCHANGED)
        # -------------------------
        if self.controller.beam_button:
            bullet_x = (
                self.starship.x
                + self.starship.width // 2
                - Bullet.DEFAULT_WIDTH // 2
            )
            bullet_y = self.starship.y

            new_bullet = Bullet(bullet_x, bullet_y)
            self.player_bullets.append(new_bullet)

            for beam in list(self.player_bullets):
                beam.update()
                if beam.y + beam.height < 0:
                    self.player_bullets.remove(beam)

            print(f"player_bullets count = {len(self.player_bullets)}")

        for beam in self.player_bullets:
            beam.update()

        # -------------------------
        # ENEMY SHOOTING (FIXED)
        # -------------------------
        self.bile_spitter.update()

        # Transfer NEW enemy bullets to the battle screen
        if self.bile_spitter.enemyBullets:
            self.enemy_bullets.extend(self.bile_spitter.enemyBullets)
            self.bile_spitter.enemyBullets.clear()

        # Update enemy bullets and remove off-screen
        for bullet in list(self.enemy_bullets):
            bullet.update()

            if bullet.y > window_height:
                self.enemy_bullets.remove(bullet)

    def draw(self, state):
        state.DISPLAY.fill(GlobalConstants.BLACK)

        self.starship.draw(state.DISPLAY)
        self.bile_spitter.draw(state.DISPLAY)

        # draw player bullets
        for beam in self.player_bullets:
            beam.draw(state.DISPLAY)

        # draw enemy bullets
        for bullet in self.enemy_bullets:
            bullet.draw(state.DISPLAY)

        pygame.display.flip()
