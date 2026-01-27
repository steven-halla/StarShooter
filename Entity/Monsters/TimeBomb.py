import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Weapons.Bullet import Bullet


class TimeBomb(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # appearance
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED

        # gameplay
        self.enemyHealth: int = 1
        self.moveSpeed: float = 0.4   # 🔑 REQUIRED OR IT WILL NOT MOVE'
        self.bullet_damage = 0

        self.spore_flower_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.spore_flower_image  # 🔑 REQUIRED

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update(self, state) -> None:
        super().update(state)
        print("f;djfas")

        # 🔑 FORCE OBJECTIVE ENTITY ACTIVE
        self.is_active = True

        # random drifting movement
        self.enemy_move_random(interval_ms=3000)

        self.update_hitbox()

    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------
    def draw(self, surface: pygame.Surface, camera):
        if self.target_player and self.hitbox.colliderect(self.target_player.hitbox):
            color = (0, 0, 255)  # blue when player inside
        else:
            color = (255, 0, 0)  # red otherwise

        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, color, (hb_x, hb_y, hb_w, hb_h), 2)

    # --------------------------------------------------
    # RANDOM MOVEMENT (3s INTERVAL)
    # --------------------------------------------------
    def enemy_move_random(self, interval_ms: int) -> None:
        now = pygame.time.get_ticks()

        # lazy init (no __init__ edits)
        if not hasattr(self, "_dir"):
            self._dir = random.randint(0, 3)  # 0=left, 1=right, 2=up, 3=down
            self._next_dir_time = now + interval_ms

        # change direction on timer
        if now >= self._next_dir_time:
            self._dir = random.randint(0, 3)
            self._next_dir_time = now + interval_ms

        # MOVE via MoveRectangle (normalized, correct)
        if self._dir == 0:
            self.mover.enemy_move_left(self)
        elif self._dir == 1:
            self.mover.enemy_move_right(self)
        elif self._dir == 2:
            self.mover.enemy_move_up(self)
        elif self._dir == 3:
            self.mover.enemy_move_down(self)
