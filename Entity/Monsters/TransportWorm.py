import math
import random

import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Weapons.Bullet import Bullet


class TransportWorm(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # enemy appearance
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED

        # summoning
        self.summon_interval_ms: int = 3000
        self.last_summon_time: int = pygame.time.get_ticks()


        # gameplay
        self.enemyHealth: int = 700

        # bullets owned by this enemy


        self.spore_flower_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()


    def update(self) -> None:
        super().update()
        self.update_hitbox()

        now = pygame.time.get_ticks()

    def summon_enemy(
            self,
            enemy_classes: list[type],
            enemy_groups: dict[type, list],
            spawn_y_offset: int = 10,
            spawn_x_variance: int = 12
    ) -> None:
        if not enemy_classes:
            return

        enemy_class = random.choice(enemy_classes)

        if enemy_class not in enemy_groups:
            return  # safety: class not wired to a group

        enemy = enemy_class()

        # Spawn near the worm with slight spread
        enemy.x = self.x + random.randint(-spawn_x_variance, spawn_x_variance)
        enemy.y = self.y + spawn_y_offset

        # REQUIRED wiring
        enemy.camera = self.camera
        enemy.target_player = self.target_player

        enemy.update_hitbox()

        enemy_groups[enemy_class].append(enemy)


    def draw(self, surface: pygame.Surface, camera):

        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.spore_flower_image.subsurface(sprite_rect)

        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)
        surface.blit(scaled_sprite, (screen_x, screen_y))

        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)
