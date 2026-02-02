import pygame
import math

from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class WaspStinger(Enemy):
    def __init__(self):
        super().__init__()

        # movement helper (SAME PATTERN AS DRONE)
        self.mover: MoveRectangle = MoveRectangle()
        self.camera = None
        self.target_player = None
        self.has_locked = False
        self.charge_dx = 0.0
        self.charge_dy = 0.0
        self.charge_cooldown = Timer(2.0)  # 2 seconds

        # state
        self.is_on_screen = False


        # stats
        self.enemyHealth: int = 100
        self.maxHealth: int = 100
        self.enemy_speed: float = 2.5
        self.width: int = 16
        self.height: int = 16

        # sprite
        self.wasp_stinger_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.wasp_stinger_image  # 🔑 REQUIRED

    def update(self,state):
        super().update(state)

        if self.camera is None or self.target_player is None:
            return

        self.update_hitbox()

        self.is_on_screen = self.mover.enemy_on_screen(self, self.camera)
        if not self.is_on_screen:
            return

        # cooldown gate AFTER a charge
        if self.has_locked and self.charge_dx == 0 and self.charge_dy == 0:
            if not self.charge_cooldown.is_ready():
                return
            else:
                self.has_locked = False

        # lock direction once
        if not self.has_locked:
            dx = self.target_player.x - self.x
            dy = self.target_player.y - self.y
            dist = max(1, (dx * dx + dy * dy) ** 0.5)

            self.charge_dx = dx / dist
            self.charge_dy = dy / dist
            self.has_locked = True

        # move
        self.x += self.charge_dx * self.enemy_speed
        self.y += self.charge_dy * self.enemy_speed

        # screen bounds in WORLD space
        left_edge = 0
        right_edge = self.camera.window_width / self.camera.zoom
        top_edge = self.camera.y
        bottom_edge = self.camera.y + (self.camera.window_height / self.camera.zoom)

        hit_edge = False

        if self.x < left_edge:
            self.x = left_edge
            hit_edge = True
        elif self.x + self.width > right_edge:
            self.x = right_edge - self.width
            hit_edge = True

        if self.y < top_edge:
            self.y = top_edge
            hit_edge = True
        elif self.y + self.height > bottom_edge:
            self.y = bottom_edge - self.height
            hit_edge = True

        # STOP once edge is hit
        if hit_edge:
            self.charge_dx = 0
            self.charge_dy = 0


        self.update_hitbox()
    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)  # 🔑 REQUIRED

        sprite_rect = pygame.Rect(60, 128, 32, 32)
        sprite = self.wasp_stinger_image.subsurface(sprite_rect)

        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        surface.blit(scaled_sprite, (screen_x, screen_y))

        # DEBUG HITBOX
        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)
