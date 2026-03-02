import random

import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class Coins(Enemy):
    def __init__(self) -> None:
        super().__init__()


        # enemy appearance
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED




        # gameplay stats (not used yet)
        self.enemyHealth: int = 1
        self.is_active = True







        self.coins_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.coins_image  # 🔑 REQUIRED

    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return

        self.update_hitbox()
        self.check_player_collision(state)




    def draw(self, surface: pygame.Surface, camera):
        # Don't draw if not active (e.g., removed due to collision with UI panel)
        if not self.is_active:
            return

        super().draw(surface, camera)  # 🔑 REQUIRED

        sprite_rect = pygame.Rect(202, 70, 32, 32)
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

    def _clamp_vertical(self) -> None:
        if self.camera is None:
            return

        gameplay_bottom = (
                self.camera.y
                + (self.camera.window_height / self.camera.zoom)
                + 20
        )

        if self.y + self.height >= gameplay_bottom:
            self.is_active = False
            self.enemyHealth = 0

    def check_player_collision(self, state) -> None:
        player = state.starship
        if player and self.hitbox.colliderect(player.hitbox):
            self.is_active = False
            self.enemyHealth = 0

    def clamp_vertical(self) -> None:
        pass
