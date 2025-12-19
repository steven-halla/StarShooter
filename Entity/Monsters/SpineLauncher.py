import math
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Weapons.Bullet import Bullet


class SpineLauncher(Enemy):
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
        self.fire_interval_ms: int = 2000
        self.last_shot_time: int = pygame.time.get_ticks()

        # gameplay
        self.enemyHealth: int = 10

        # bullets owned by this enemy
        self.enemyBullets: list[Bullet] = []


        self.spore_flower_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    def shoot_spines(self) -> None:
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2



        # DOWN bullet
        bullet_down = Bullet(cx, cy)
        bullet_down.dx = 0
        bullet_down.speed = self.weapon_speed

        bullet_down.width = self.bulletWidth
        bullet_down.height = self.bulletHeight
        bullet_down.color = self.bulletColor
        bullet_down.damage = 10

        self.enemyBullets.append(bullet_down)
    def update(self) -> None:
        super().update()
        self.update_hitbox()

        now = pygame.time.get_ticks()

        if now - self.last_shot_time >= self.fire_interval_ms:
            self.shoot_spines()
            self.last_shot_time = now

        for bullet in self.enemyBullets:
            bullet.update()

            print(
                "➡️ BULLET MOVING",
                "x:", bullet.x,
                "y:", bullet.y,
                "speed:", bullet.speed,
                "diag_speed_y:", bullet.diag_speed_y
            )
    def draw(self, surface: pygame.Surface, camera):
        print("🎨 DRAW SPORE FLOWER — bullets:", len(self.enemyBullets))

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
