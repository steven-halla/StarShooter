import random
import math
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy


class TransportWorm(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # -------------------------
        # APPEARANCE
        # -------------------------
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED

        self.sprite_sheet = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.sprite_sheet  # 🔑 REQUIRED

        # -------------------------
        # GAMEPLAY
        # -------------------------
        self.enemyHealth: int = 700

        # -------------------------
        # SUMMONING
        # -------------------------
        self.summon_interval_ms: int = 4100
        self.last_summon_time: int = pygame.time.get_ticks()

        self.summon_level: int = 0
        self.burning: bool = False   # Napalm disables summoning
        self.about_to_summon: bool = False
        self.is_active = False

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
    def update(self) -> None:
        super().update()
        if not self.is_active:
            return

        self.update_hitbox()


        self.update_hitbox()



    # -------------------------------------------------
    # SUMMON LOGIC
    # -------------------------------------------------
    def summon_enemy(
        self,
        enemy_classes: list[type],
        enemy_groups: dict[type, list],
        spawn_y_offset: int = 18,
        spawn_x_variance: int = 14
    ) -> None:
        """
        Spawns ONE enemy near the worm.
        Caller controls WHEN this runs.
        """

        if self.burning:
            return

        if not enemy_classes:
            return

        # Weighted selection (order must match enemy_classes)
        enemy_class = random.choices(
            enemy_classes,
            weights=[4, 2, 3, 2],  # adjust as needed
            k=1
        )[0]

        if enemy_class not in enemy_groups:
            return

        enemy = enemy_class()

        # Spread spawn
        angle = random.uniform(-0.6, 0.6)
        radius = random.randint(6, spawn_x_variance)

        enemy.x = self.x + int(math.sin(angle) * radius)
        enemy.y = self.y + spawn_y_offset

        # REQUIRED wiring
        enemy.camera = self.camera
        enemy.target_player = self.target_player

        enemy.update_hitbox()

        enemy_groups[enemy_class].append(enemy)

        # Escalation
        self.summon_level += 1

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------
    def draw(self, surface: pygame.Surface, camera) -> None:
        super().draw(surface, camera)  # 🔑 REQUIRED

        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.sprite_sheet.subsurface(sprite_rect)

        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)
        surface.blit(scaled_sprite, (screen_x, screen_y))

        # Hitbox debug
        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * scale)
        hb_h = int(self.hitbox.height * scale)

        pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)
