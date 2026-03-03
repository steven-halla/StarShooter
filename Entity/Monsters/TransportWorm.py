import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class TransportWorm(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement
        self.mover: MoveRectangle = MoveRectangle()
        self.move_direction: int = random.choice([-1, 1])
        self.moveSpeed: float = 2.2
        self.edge_padding: int = 0

        # identity / visuals
        self.name: str = "Transport Worm"
        self.width: int = 40
        self.height: int = 40
        self.color = GlobalConstants.RED

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image

        # stats
        self.enemyHealth: float = 150.0
        self.maxHealth: float = 150.0
        self.exp: int = 1
        self.credits: int = 5

        # ranged attack
        self.bulletColor = GlobalConstants.SKYBLUE
        self.attack_timer = Timer(3.0)

        # touch damage
        self.touch_damage: int = 10
        self.touch_timer = Timer(0.75)

        # -------------------------
        # SUMMONING
        # -------------------------
        self.summon_interval_ms: int = 6000
        self.last_summon_time: int = 0 # Start ready

        self.summon_level: int = 0
        self.burning: bool = False  # Napalm disables summoning
        self.about_to_summon: bool = False
        self.is_active = False

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
        weights = [4, 2, 3, 2]
        if len(enemy_classes) != len(weights):
            weights = [1] * len(enemy_classes)

        enemy_class = random.choices(
            enemy_classes,
            weights=weights,  # adjust as needed
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

        # DEBUG PRINT
        if hasattr(self, 'camera') and self.camera:
            s_x = self.camera.world_to_screen_x(enemy.x)
            s_y = self.camera.world_to_screen_y(enemy.y)
            print(f"[SUMMON] {enemy_class.__name__} at Screen: ({s_x:.1f}, {s_y:.1f})")

        # Escalation
        self.summon_level += 1

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
    def update(self, state) -> None:
        self.update_hitbox()

        # check distance to player
        player = state.starship
        dist_y = abs(player.y - self.y)
        if dist_y < 1000:
            self.is_active = True
        else:
            self.is_active = False

        if not self.is_active:
            return

        # 🔑 CALL TOUCH DAMAGE HANDLER
        self.player_collide_damage(state.starship)

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------
    def draw(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        super().draw(surface, camera)

        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.bile_spitter_image.subsurface(sprite_rect)

        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        surface.blit(
            scaled_sprite,
            (
                camera.world_to_screen_x(self.x),
                camera.world_to_screen_y(self.y),
            )
        )

    def clamp_vertical(self) -> None:
        pass
