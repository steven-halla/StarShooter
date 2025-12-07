import pygame
import random

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class KamikazeDrone(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement helper
        self.mover: MoveRectangle = MoveRectangle()

        # appearance
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED

        # movement stats
        self.speed: float = 5.0

        # gameplay stats
        self.enemyHealth: int = 5
        self.exp: int = 1
        self.credits: int = 5

        # kamikaze-specific
        self.target_player = None     # will be assigned externally
        self.is_exploding = False     # state toggle for explosion
        self.explosion_damage: int = 50  # huge damage on hit

        self.kamikaze_drone_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    def update(self):
        """Move toward the player and detect collision."""
        self.update_hitbox()

        if self.target_player is None:
            return  # no target yet

        # --- Convert positions to world space ---
        px = self.target_player.x
        py = self.target_player.y

        # direction vector toward player
        dx = px - self.x
        dy = py - self.y

        dist = max(1, (dx * dx + dy * dy) ** 0.5)

        # normalize direction
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

        self.update_hitbox()

        # explosion check
        if self.hitbox.colliderect(self.target_player.hitbox):
            self.is_exploding = True
            self.enemyHealth = 0  # mark for removal

    def draw(self, surface: pygame.Surface, camera):
        sprite_rect = pygame.Rect(10, 425, 32, 32)
        sprite = self.kamikaze_drone_image.subsurface(sprite_rect)

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
