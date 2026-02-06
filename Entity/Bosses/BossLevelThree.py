import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class BossLevelThree(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement
        self.mover: MoveRectangle = MoveRectangle()
        self.move_direction: int = random.choice([-1, 1])
        self.moveSpeed: float = 2.2
        self.edge_padding: int = 0

        # identity / visuals
        self.name: str = "BossLevelThree"
        self.width: int = 40
        self.height: int = 40
        self.color = GlobalConstants.RED

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image

        # stats
        self.enemyHealth: float = 2000.0
        self.maxHealth: float = 2000.0
        self.exp: int = 1
        self.credits: int = 5

        # ranged attack
        self.bulletColor = GlobalConstants.SKYBLUE

        # touch damage
        self.touch_damage: int = 10
        self.touch_timer = Timer(0.75)

        # rope
        self._rope = None
        self.player_caught: bool = False

        # -------------------------
        # PHASE SYSTEM
        # -------------------------
        self.phase = 1

        self.phase1_rope_timer = Timer(5.0)
        self.phase1_shoot_timer = Timer(2.0)

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
    def update(self, state) -> None:
        super().update(state)

        if not self.is_active or self.camera is None:
            return

        self.update_hitbox()

        # PHASE SELECTION BY HP
        # PHASE SELECTION BY HP (EXPLICIT THRESHOLDS)
        if self.enemyHealth > 1200:
            self.phase = 1
        elif self.enemyHealth > 600:
            self.phase = 2
        else:
            self.phase = 3

        if self.phase == 1:
            self.phase_one(state)
        elif self.phase == 2:
            self.phase_two(state)
        elif self.phase == 3:
            self.phase_three(state)

        self.check_rope_collision(self.target_player)

    # -------------------------------------------------
    # PHASES
    # -------------------------------------------------
    def phase_one(self, state) -> None:
        # ALWAYS update rope if it exists
        if self._rope is not None:
            self.rope_grab(
                rope_length=160,
                rope_width=4,
                rope_speed=3.0,
                rope_color=(180, 180, 180),
                state=state
            )

        # TIMER: start rope
        if self.phase1_rope_timer.is_ready() and self._rope is None:
            self.rope_grab(
                rope_length=160,
                rope_width=4,
                rope_speed=3.0,
                rope_color=(180, 180, 180),
                state=state
            )
            self.phase1_rope_timer.reset()

        # TIMER: shoot
        if self.phase1_shoot_timer.is_ready():
            self.shoot_single_down_vertical_y(
                bullet_speed=4.0,
                bullet_width=20,
                bullet_height=20,
                bullet_color=self.bulletColor,
                bullet_damage=10,
                state=state
            )
            self.phase1_shoot_timer.reset()

    def phase_two(self, state) -> None:
        pass

    def phase_three(self, state) -> None:
        pass

    # -------------------------------------------------
    # MOVEMENT
    # -------------------------------------------------
    def moveAI(self) -> None:
        window_width = GlobalConstants.BASE_WINDOW_WIDTH

        if not hasattr(self, "_last_x"):
            self._last_x = self.x

        if self.move_direction > 0:
            self.mover.enemy_move_right(self)
        else:
            self.mover.enemy_move_left(self)

        if self.x < self.edge_padding:
            self.x = self.edge_padding
        elif self.x + self.width > window_width - self.edge_padding:
            self.x = window_width - self.edge_padding - self.width

        if self.x == self._last_x:
            self.move_direction *= -1

        self._last_x = self.x

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------
    def draw(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        self.draw_rope(surface, camera)
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

    # -------------------------------------------------
    # ROPE COLLISION
    # -------------------------------------------------
    def check_rope_collision(self, player) -> None:
        if player is None or self._rope is None:
            return

        rope = self._rope
        thickness = rope.width

        x1, y1 = rope.start.x, rope.start.y
        x2, y2 = rope.end.x, rope.end.y

        rope_rect = pygame.Rect(
            min(x1, x2) - thickness,
            min(y1, y2) - thickness,
            abs(x2 - x1) + thickness * 2,
            abs(y2 - y1) + thickness * 2
        )

        if rope_rect.colliderect(player.melee_hitbox):
            self.player_caught = True
        else:
            self.player_caught = False
