import math
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

        # bullet appearance
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20

        # firing
        self.weapon_speed: float = 3.0
        self.fire_interval_ms: int = 3000
        self.last_shot_time: int = pygame.time.get_ticks()

        # gameplay
        self.enemyHealth: int = 3000

        # bullets owned by this enemy
        self.enemyBullets: list[Bullet] = []


        self.spore_flower_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()


    def update(self) -> None:
        super().update()
        self.update_hitbox()

        now = pygame.time.get_ticks()






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
