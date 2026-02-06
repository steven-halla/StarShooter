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
        self.attack_timer = Timer(3.0)

        # touch damage
        self.touch_damage: int = 10
        self.touch_timer = Timer(0.75)
        self._rope = None
        self.player_caught: bool = False

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
    def update(self, state) -> None:
        super().update(state)

        if not self.is_active or self.camera is None:
            return

        self.update_hitbox()

        # ROPE ATTACK
        # spawn rope every 3s
        # =============================
        # LEVEL 3 ROPE CONTROL (FIXED)
        # =============================

        now = pygame.time.get_ticks()

        # local init only (NO __init__ edits)
        if not hasattr(self, "_rope_was_active"):
            self._rope_was_active = False

        if not hasattr(self, "_rope_next_allowed_time"):
            self._rope_next_allowed_time = 0

        ROPE_DURATION_MS = 3000
        ROPE_COOLDOWN_MS = 4000

        # -----------------------------
        # START ROPE (only if allowed)
        # -----------------------------
        if self._rope is None and now >= self._rope_next_allowed_time:
            self.rope_grab(
                rope_length=160,
                rope_width=4,
                rope_speed=3.0,
                rope_duration_ms=ROPE_DURATION_MS,
                rope_color=(180, 180, 180),
                state=state
            )

        # -----------------------------
        # UPDATE ROPE (every frame)
        # -----------------------------
        if self._rope is not None:
            self.rope_grab(
                rope_length=160,
                rope_width=4,
                rope_speed=3.0,
                rope_duration_ms=ROPE_DURATION_MS,
                rope_color=(180, 180, 180),
                state=state
            )
            self._rope_was_active = True

        # -----------------------------
        # ROPE JUST ENDED → START COOLDOWN
        # -----------------------------
        if self._rope is None and self._rope_was_active:
            self._rope_next_allowed_time = now + ROPE_COOLDOWN_MS
            self._rope_was_active = False


        # LOCAL fire-rate gate (NO __init__ fields)
        now = pygame.time.get_ticks()

        if not hasattr(self, "_phase1_shoot_next_time"):
            self._phase1_shoot_next_time = 0

        if now >= self._phase1_shoot_next_time:
            self.shoot_single_down_vertical_y(
                bullet_speed=4.0,
                bullet_width=20,
                bullet_height=20,
                bullet_color=self.bulletColor,
                bullet_damage=10,
                state=state
            )
            self._phase1_shoot_next_time = now + 2000  # 2 seconds



        # Check rope collision with player
        self.check_rope_collision(self.target_player)


    # -------------------------------------------------
    # TOUCH DAMAGE (STANDALONE FUNCTION)
    # -------------------------------------------------

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
        self.check_rope_collision(self.target_player)

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

        # 🔑 USE MELEE HITBOX (ACTIVE PLAYER RECT)
        if rope_rect.colliderect(player.melee_hitbox):
            print("ROPE HIT PLAYER")
            self.player_caught = True
        else:
            self.player_caught = False
