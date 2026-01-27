import math
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Weapons.Bullet import Bullet


# in future shold damage player for 10 shields, but nothing if no shields

class TimeBomb(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # enemy appearance
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED

        # gameplay
        self.enemyHealth: int = 1

        self.spore_flower_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.spore_flower_image  # 🔑 REQUIRED


    def update(self, state) -> None:
        super().update(state)
        self.update_hitbox()
        # print(f"Rescue Pod HP: {self.enemyHealth}")?

    def draw(self, surface: pygame.Surface, camera, state):
        # Determine color based on collision with player
        if self.hitbox.colliderect(state.starship.hitbox):
            color = (0, 0, 255)  # blue
        else:
            color = (255, 0, 0)  # red

        # Convert hitbox to screen space
        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, color, (hb_x, hb_y, hb_w, hb_h), 2)


    # def draw(self, surface: pygame.Surface, camera):
    #     super().draw(surface, camera)  # 🔑 REQUIRED
    #
    #     sprite_rect = pygame.Rect(10, 267, 32, 32)
    #     sprite = self.spore_flower_image.subsurface(sprite_rect)
    #
    #     scale = camera.zoom
    #     scaled_sprite = pygame.transform.scale(
    #         sprite,
    #         (int(self.width * scale), int(self.height * scale))
    #     )
    #
    #     screen_x = camera.world_to_screen_x(self.x)
    #     screen_y = camera.world_to_screen_y(self.y)
    #     surface.blit(scaled_sprite, (screen_x, screen_y))
    #
    #     hb_x = camera.world_to_screen_x(self.hitbox.x)
    #     hb_y = camera.world_to_screen_y(self.hitbox.y)
    #     hb_w = int(self.hitbox.width * camera.zoom)
    #     hb_h = int(self.hitbox.height * camera.zoom)
    #
    #     pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)
