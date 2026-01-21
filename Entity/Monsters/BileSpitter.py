import random
import pygame
from pygame import surface

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Entity.Monsters.RescuePod import RescuePod
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
        self.fire_interval_ms: int = 2000
        self.last_shot_time: int = 0
        self.speed: float = 0.4
        self.enemyHealth: int = 20
        self.exp: int = 1
        self.credits: int = 5
        # No longer using self.enemyBullets - using game_state.enemy_bullets instead
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
        self.moveAI()

        # WORLD-SPACE hitbox
        self.update_hitbox()

        # example call (inside enemy update)
        # =========================
        # CALL (inside enemy update)
        # =========================



        # firing
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.fire_interval_ms:

            self.explosive_egg_system(
                width=20,
                height=20,
                explosion_timer_ms=3000,  # Ensure explosion persists for exactly 3 seconds
                explosion_radius=100,     # Make explosion significantly bigger than the egg
                damage=40,
                distance=200,  # 0 = laid bomb
                speed=0,       # 0 if laid
                state=state
            )
            # BileSpitter.update (or wherever it’s called)
            # self.create_bomb(64, 64)



            self.last_shot_time = now

        # No longer need to update bullets here as they are managed by the game state


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
        self.draw_bomb(surface, self.camera)
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
