import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BileSpitter(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20
        self.bileSpeed: int = 2
        self.fire_interval_ms: int = 3000
        self.last_shot_time: int = 0
        self.speed: float = 0.4
        self.enemyHealth: int = 20
        self.exp: int = 1
        self.credits: int = 5
        # self.enemyBullets: list[Bullet] = []
        self.moveSpeed: float = 1.2
        self.edge_padding: int = 30
        self.move_direction: int = random.choice([-1, 1])
        self.move_interval_ms: int = 3000
        self.last_move_toggle: int = pygame.time.get_ticks()
        self.is_moving: bool = True

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image


    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return


        # WORLD-SPACE hitbox
        self.update_hitbox()

        # movement AI (UNCHANGED)
        self.moveAI()
        self.touch_mellee(
            bullet_width=40,
            bullet_height=40,
            bullet_color=GlobalConstants.RED,
            bullet_damage=11
        )


        # firing
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.fire_interval_ms:
            # self.shoot_single_bullet_aimed_at_player(
            #     bullet_speed=4.0,
            #     bullet_width=20,
            #     bullet_height=20,
            #     bullet_color=self.bulletColor,
            #     bullet_damage=10
            # )

            self.last_shot_time = now

        # update bullets (WORLD SPACE ONLY)
        for bullet in self.enemyBullets[:]:
            bullet.x += bullet.vx * bullet.bullet_speed
            bullet.y += bullet.vy * bullet.bullet_speed
            bullet.update_rect()


    def moveAI(self) -> None:
        window_width = GlobalConstants.BASE_WINDOW_WIDTH

        if not hasattr(self, "_last_x"):
            self._last_x = self.x

        if self.move_direction > 0:
            self.mover.enemy_move_right(self)
        else:
            self.mover.enemy_move_left(self)

        if self.x < self.edge_padding:
            self.x = self.edge_padding
        elif self.x + self.width > window_width - self.edge_padding:
            self.x = window_width - self.edge_padding - self.width

        if self.x == self._last_x:
            self.move_direction *= -1
            if self.move_direction > 0:
                self.mover.enemy_move_right(self)
            else:
                self.mover.enemy_move_left(self)

        self._last_x = self.x

    def draw(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        super().draw(surface, camera)

        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.bile_spitter_image.subsurface(sprite_rect)

        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)
        surface.blit(scaled_sprite, (screen_x, screen_y))

    def _clamp_vertical(self) -> None:
        pass
