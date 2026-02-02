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
        self.camera = None

        # appearance
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED

        # movement stats
        self.speed: float = 2.0

        # gameplay stats
        self.enemyHealth: int = 30
        self.maxHealth: int = 30
        self.exp: int = 1
        self.credits: int = 5

        # kamikaze-specific
        self.target_player = None     # will be assigned externally
        self.is_exploding = False     # state toggle for explosion
        self.explosion_damage: int = 20  # huge damage on hit

        self.kamikaze_drone_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.kamikaze_drone_image  # 🔑 REQUIRED

        self.is_on_screen = False

    def update(self, state):
        super().update(state)

        self.update_hitbox()

        # check if visible first
        self.is_on_screen = self.mover.enemy_on_screen(self, self.camera)

        # do NOT track if drone is not yet visible
        if not self.is_on_screen:
            return

        if self.target_player is None:
            return

        # direction vector toward player
        px = self.target_player.x
        py = self.target_player.y

        dx = px - self.x
        dy = py - self.y
        dist = max(1, (dx * dx + dy * dy) ** 0.5)

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

        self.update_hitbox()

        # explosion check
        if self.hitbox.colliderect(self.target_player.hitbox):
            self.on_hit_player()


    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)  # 🔑 REQUIRED

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

    def on_hit_player(self):

        """Handle drone impact damage (player or non-player target)."""
        if self.target_player is None:
            return

        # Player target
        if hasattr(self.target_player, "shipHealth"):
            self.target_player.shipHealth -= self.explosion_damage
            if hasattr(self.target_player, "on_hit"):
                self.target_player.on_hit()

        # Non-player target (e.g., SpaceStation)
        elif hasattr(self.target_player, "hp"):
            self.target_player.hp -= self.explosion_damage

        self.enemyHealth = 0  # mark for removal
