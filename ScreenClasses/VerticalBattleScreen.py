import pygame
from pygame import Surface

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Controller.KeyBoardControls import KeyBoardControls
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.StarShip import StarShip
from Movement.MoveRectangle import MoveRectangle
from ScreenClasses.Camera import Camera
from Weapons.Bullet import Bullet


class VerticalBattleScreen:
    def __init__(self):
        self.starship: StarShip = StarShip()
        self.isStart: bool = True
        self.playerDead: bool = False
        self.mover: MoveRectangle = MoveRectangle()
        self.controller: KeyBoardControls = KeyBoardControls()
        self.STARSHIP_HORIZONTAL_CENTER_DIVISOR: int = 2
        self.STARSHIP_BOTTOM_OFFSET: int = 100
        self.MIN_X: int = 0
        self.MIN_Y: int = 0
        self.scrollScreen: bool = False

        self.ENEMY_HORIZONTAL_CENTER_DIVISOR: int = 2
        self.ENEMY_TOP_OFFSET: int = 50
        self.was_q_pressed_last_frame: bool = False

        self.player_bullets: list = []
        self.enemy_bullets: list = []     # All enemy bullets go here

        self.WORLD_HEIGHT: int = GlobalConstants.WINDOWS_SIZE[1] * 3
        self.SCROLL_SPEED_PER_SECOND: float = 100.0
        self.camera_y: float = 0.0
        self.SCROLL_SPEED_PER_FRAME: float = 111.0

        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        self.camera = Camera(
            window_width=window_width,
            window_height=window_height,
            world_height=self.WORLD_HEIGHT,
            scroll_speed_per_frame=self.SCROLL_SPEED_PER_FRAME,
            initial_zoom=2.0,
        )

        # IMPORTANT: we no longer have a default enemy
        # Level classes (like LevelOne) define bileSpitterGroup
        # so VerticalBattleScreen does NOT create enemies here.


    def start(self, state):
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        self.starship.x = window_width // self.STARSHIP_HORIZONTAL_CENTER_DIVISOR
        self.starship.y = window_height - self.STARSHIP_BOTTOM_OFFSET


    def clamp_starship_to_screen(self) -> None:
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        zoom = self.camera.zoom

        visible_width = window_width / zoom
        visible_height = window_height / zoom

        max_x = visible_width - self.starship.width
        max_y = visible_height - self.starship.height

        if self.starship.x < self.MIN_X:
            self.starship.x = self.MIN_X
        elif self.starship.x > max_x:
            self.starship.x = max_x

        if self.starship.y < self.MIN_Y:
            self.starship.y = self.MIN_Y
        elif self.starship.y > max_y:
            self.starship.y = max_y


    def update(self, state):
        if self.starship.shipHealth <= 0:
            self.playerDead = True

        if self.isStart:
            self.start(state)
            self.isStart = False

        self.controller.update()

        if not self.playerDead:
            if self.controller.left_button:
                self.mover.player_move_left(self.starship)
            if self.controller.right_button:
                self.mover.player_move_right(self.starship)
            if self.controller.up_button:
                self.mover.player_move_up(self.starship)
            if self.controller.down_button:
                self.mover.player_move_down(self.starship)

            if self.controller.q_button and not self.was_q_pressed_last_frame:
                self.scrollScreen = not self.scrollScreen

        self.was_q_pressed_last_frame = self.controller.q_button

        self.clamp_starship_to_screen()
        if not self.playerDead:
            self.starship.update()

        # -------------------------
        # PLAYER SHOOTING
        # -------------------------
        if (
            self.controller.main_weapon_button and
            self.starship.bullet_timer.is_ready() and
            not self.playerDead
        ):
            center_x = self.starship.x + self.starship.width // 2 + 14
            bullet_y = self.starship.y

            spread = self.starship.bullet_spread_offset
            count = self.starship.bullets_per_shot
            start_index = -(count // 2)

            for i in range(count):
                offset = (start_index + i) * spread
                bullet_x = center_x + offset - Bullet.DEFAULT_WIDTH // 2

                new_bullet = Bullet(bullet_x, bullet_y)
                self.player_bullets.append(new_bullet)

            self.starship.bullet_timer.reset()

        # Move player bullets
        for bullet in list(self.player_bullets):
            bullet.update()
            if bullet.y + bullet.height < 0:
                self.player_bullets.remove(bullet)

        # -------------------------
        # ENEMY UPDATE + SHOOTING
        # -------------------------
        if hasattr(self, "bileSpitterGroup"):
            for enemy in self.bileSpitterGroup:
                enemy.update()
                # Transfer bullets from each enemy
                if enemy.enemyBullets:
                    self.enemy_bullets.extend(enemy.enemyBullets)
                    enemy.enemyBullets.clear()

        # -------------------------
        # BULLET COLLISION (PLAYER → ENEMY)
        # -------------------------
        for bullet in list(self.player_bullets):
            bullet.update()
            if bullet.y + bullet.height < 0:
                self.player_bullets.remove(bullet)
                continue

            if hasattr(self, "bileSpitterGroup"):
                for enemy in list(self.bileSpitterGroup):
                    enemy.update_hitbox()
                    if bullet.collide_with_rect(enemy.hitbox):
                        enemy.enemyHealth -= self.starship.bulletDamage

                        if not bullet.is_active:
                            self.player_bullets.remove(bullet)

                        if enemy.enemyHealth <= 0:
                            self.bileSpitterGroup.remove(enemy)

                        break

        # -------------------------
        # ENEMY BULLETS → PLAYER
        # -------------------------
        _, window_height = GlobalConstants.WINDOWS_SIZE

        for bullet in list(self.enemy_bullets):
            bullet.update()

            if bullet.y > window_height:
                self.enemy_bullets.remove(bullet)
                continue

            if bullet.collide_with_rect(self.starship.hitbox):
                self.starship.shipHealth -= bullet.damage
                self.starship.on_hit()

                if not bullet.is_active:
                    self.enemy_bullets.remove(bullet)


    def draw(self, state) -> None:
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        zoom = self.camera.zoom

        scene_surface = pygame.Surface((window_width, window_height))

        self.draw_background(scene_surface)

        if not self.playerDead:
            self.starship.draw(scene_surface)

        if hasattr(self, "bileSpitterGroup"):
            for enemy in self.bileSpitterGroup:
                enemy.draw(scene_surface)

        for bullet in self.player_bullets:
            bullet.draw(scene_surface)

        for bullet in self.enemy_bullets:
            bullet.draw(scene_surface)

        scaled_width = int(window_width * zoom)
        scaled_height = int(window_height * zoom)
        scaled_scene = pygame.transform.scale(
            scene_surface, (scaled_width, scaled_height)
        )

        state.DISPLAY.fill(GlobalConstants.BLACK)
        state.DISPLAY.blit(scaled_scene, (0, 0))


    def draw_background(self, surface: Surface) -> None:
        self.draw_scrolling_background(surface)


    def update_camera_scroll(self, state) -> None:
        _, window_height = GlobalConstants.WINDOWS_SIZE

        max_camera_y = self.WORLD_HEIGHT - window_height
        min_camera_y = 0.0

        self.camera_y = max(min_camera_y, self.camera_y - self.SCROLL_SPEED_PER_FRAME)


    def draw_scrolling_background(self, surface: "Surface") -> None:
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        top_world_y = self.camera_y
        bottom_world_y = self.camera_y + window_height
