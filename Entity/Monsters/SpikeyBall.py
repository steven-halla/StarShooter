import random

import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class SpikeyBall(Enemy):
    def __init__(self) -> None:
        super().__init__()


        # enemy appearance
        self.width: int = 40
        self.height: int = 40
        self.name: str = "SpikeyBall"
        self.color: tuple[int, int, int] = GlobalConstants.RED




        # gameplay stats (not used yet)
        self.enemyHealth: int = 50
        self.maxHealth: int = 50
        self.is_active = True

        self.coins_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.coins_image  # 🔑 REQUIRED   # touch damage
        self.touch_damage: int = 50
        self.touch_timer = Timer(0.75)


    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return
        self.update_hitbox()

        # print("BILE:", self.y, "CAM:", self.camera.y,
        #       "SCREEN_Y:", self.camera.world_to_screen_y(self.y))

        """Handle firing every 3 seconds + move bullets."""

        now = pygame.time.get_ticks()


    def draw(self, surface: pygame.Surface, camera):
        # Don't draw if not active (e.g., removed due to collision with UI panel)
        if not self.is_active:
            return

        super().draw(surface, camera)  # 🔑 REQUIRED

        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.coins_image.subsurface(sprite_rect)

        # scale ship with zoom
        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        # convert world → screen
        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        # draw ship
        surface.blit(scaled_sprite, (screen_x, screen_y))

        # ================================
        #  DRAW PLAYER HITBOX (DEBUG)
        # ================================
        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)

    def clamp_vertical(self) -> None:
        pass
