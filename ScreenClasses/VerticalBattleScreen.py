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
        self.scrollScreen: bool = False

        self.bile_spitter: BileSpitter = BileSpitter()
        self.ENEMY_HORIZONTAL_CENTER_DIVISOR: int = 2
        self.ENEMY_TOP_OFFSET: int = 50

        self.player_bullets: list = []
        self.enemy_bullets: list = []   # Bullet objects ONLY

        self.WORLD_HEIGHT: int = GlobalConstants.WINDOWS_SIZE[1] * 3  # 3 screens tall
        self.SCROLL_SPEED_PER_SECOND: float = 100.0
        self.camera_y: float = 0.0

        self.BAND_COLORS: list[tuple[int, int, int]] = [
            GlobalConstants.PINK,
            GlobalConstants.GREY,
            GlobalConstants.BLACK,
        ]

        self.WORLD_HEIGHT: int = GlobalConstants.WINDOWS_SIZE[1] * 3  # 3 screens tall

        # scrolling
        self.SCROLL_SPEED_PER_FRAME: float = 2.0  # same as: scroll_speed = 2.0
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        # start at the BOTTOM of the world
        self.camera_y: float = self.WORLD_HEIGHT - window_height



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
            print("Pew")
            self.mover.player_move_left(self.starship)
        if self.controller.right_button:
            self.mover.player_move_right(self.starship)
        if self.controller.up_button:
            self.mover.player_move_up(self.starship)
        if self.controller.down_button:
            self.mover.player_move_down(self.starship)
        if self.controller.q_button:
            print("Mew")

        self._clamp_starship_to_screen()

        # -------------------------
        # PLAYER BULLET LOGIC (UNCHANGED)
        # -------------------------
        if self.controller.main_weapon_button:
            bullet_x = (
                self.starship.x
                + self.starship.width // 2
                - Bullet.DEFAULT_WIDTH // 2
            )
            bullet_y = self.starship.y

            new_bullet = Bullet(bullet_x, bullet_y)
            self.player_bullets.append(new_bullet)

            for bullet in list(self.player_bullets):
                bullet.update()
                if bullet.y + bullet.height < 0:
                    self.player_bullets.remove(bullet)

            print(f"player_bullets count = {len(self.player_bullets)}")

        for bullet in self.player_bullets:
            bullet.update()

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

        # ...after bullets / enemy updates
        # inside update(...), AFTER self.controller.update()


    def draw(self, state):
        # state.DISPLAY.fill(GlobalConstants.BLACK)
        self.draw_scrolling_background(state.DISPLAY)

        self.starship.draw(state.DISPLAY)
        self.bile_spitter.draw(state.DISPLAY)

        # draw player bullets
        for bullet in self.player_bullets:
            bullet.draw(state.DISPLAY)

        # draw enemy bullets
        for bullet in self.enemy_bullets:
            bullet.draw(state.DISPLAY)

        pygame.display.flip()

    def update_camera_scroll(self, state) -> None:
        _, window_height = GlobalConstants.WINDOWS_SIZE

        max_camera_y: float = self.WORLD_HEIGHT - window_height
        min_camera_y: float = 0.0

        # move camera UP in world space (so you fly “up” the map),
        # but don’t go past the top
        self.camera_y = max(min_camera_y, self.camera_y - self.SCROLL_SPEED_PER_FRAME)

    def draw_scrolling_background(self, surface: "Surface") -> None:
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        top_world_y: float = self.camera_y
        bottom_world_y: float = self.camera_y + window_height

        band_height: float = window_height  # each band is one screen tall

        for index, color in enumerate(self.BAND_COLORS):
            band_top: float = index * band_height
            band_bottom: float = band_top + band_height

            visible_top: float = max(band_top, top_world_y)
            visible_bottom: float = min(band_bottom, bottom_world_y)

            if visible_bottom <= visible_top:
                continue

            screen_y: float = visible_top - top_world_y
            rect_height: float = visible_bottom - visible_top

            pygame.draw.rect(
                surface,
                color,
                pygame.Rect(0, int(screen_y), window_width, int(rect_height)),
            )
