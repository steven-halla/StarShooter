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
        self.moveSpeed: float = 0.8
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
        now = pygame.time.get_ticks()

        # -------------------------
        # PHASE SELECTION (EXPLICIT)
        # -------------------------
        # if self.enemyHealth > 1900:
        #     self.phase = 1
        # elif self.enemyHealth > 1700:
        #     self.phase = 2
        # else:
        #     self.phase = 3
        self.phase = 3

        # -------------------------
        # PHASE 1 — ROPE + SHOOT
        # -------------------------
        if self.phase == 1:
            # rope control (uses your working timing block)
            if not hasattr(self, "_rope_was_active"):
                self._rope_was_active = False
            if not hasattr(self, "_rope_next_allowed_time"):
                self._rope_next_allowed_time = 0

            ROPE_DURATION_MS = 3000
            ROPE_COOLDOWN_MS = 4000

            if self._rope is None and now >= self._rope_next_allowed_time:
                self.rope_grab(
                    rope_length=160,
                    rope_width=4,
                    rope_speed=3.0,
                    rope_duration_ms=ROPE_DURATION_MS,
                    rope_color=(180, 180, 180),
                    state=state
                )

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

            if self._rope is None and self._rope_was_active:
                self._rope_next_allowed_time = now + ROPE_COOLDOWN_MS
                self._rope_was_active = False

            # shooting every 2 seconds
            if not hasattr(self, "_shoot_last_time"):
                self._shoot_last_time = 0

            if now - self._shoot_last_time >= 2000:
                self.shoot_single_down_vertical_y(
                    bullet_speed=4.0,
                    bullet_width=20,
                    bullet_height=20,
                    bullet_color=self.bulletColor,
                    bullet_damage=10,
                    state=state
                )
                self._shoot_last_time = now

        # -------------------------
        # PHASE 2 — CHASE PLAYER
        # -------------------------
        # elif self.phase == 2:
        #     self.phase_two_ai(self.target_player)

        # =========================
        # PHASE 2 — BOMB ATTACK
        # =========================
        elif self.phase == 2:
            if self._rope is not None:
                if self._rope in state.enemy_bullets:
                    state.enemy_bullets.remove(self._rope)
                self._rope = None
                self.player_caught = False
            # movement: chase player
            self.phase_two_move_ai(self.target_player)

            now = pygame.time.get_ticks()

            # local init (NO __init__ edits)
            if not hasattr(self, "_phase2_bomb_last_time"):
                self._phase2_bomb_last_time = 0

            PHASE2_BOMB_INTERVAL_MS = 3000  # drop bomb every 3s

            if now - self._phase2_bomb_last_time >= PHASE2_BOMB_INTERVAL_MS:
                self.lay_bomb(
                    width=20,
                    height=20,
                    explosion_timer_ms=20000,
                    explosion_radius=10,
                    damage=40,
                    distance=0,
                    speed=4.0,
                    state=state
                )
                self._phase2_bomb_last_time = now

        # -------------------------
        # PHASE 3 — PLACEHOLDER
        # -------------------------
        elif self.phase == 3:
            self.moveSpeed = 2
            if self._rope is not None:
                if self._rope in state.enemy_bullets:
                    state.enemy_bullets.remove(self._rope)
                self._rope = None
                self.player_caught = False

            # ─────────────────────────────
            # PHASE 3 – MELEE STRIKE (4s TIMER)
            # ─────────────────────────────
            now = pygame.time.get_ticks()

            # local init (NO __init__)
            if not hasattr(self, "_melee_last_time"):
                self._melee_last_time = 0

            # bottom boundary: space station occupies bottom 100px
            SAFE_Y_MAX = GlobalConstants.BASE_WINDOW_HEIGHT - 100

            # ─────────────────────────────
            # START MELEE (every 4s)
            # ─────────────────────────────
            if not getattr(self, "_melee_active", False):
                if now - self._melee_last_time >= 4000:

                    # TEMP CLAMP ONLY FOR DIRECTION CALC
                    tx = self.target_player.x
                    ty = min(self.target_player.y, SAFE_Y_MAX)

                    dx = tx - self.x
                    dy = ty - self.y
                    dist = math.hypot(dx, dy)
                    if dist != 0:
                        self._melee_dx = dx / dist
                        self._melee_dy = dy / dist

                    self.melee_strike(
                        dash_speed=5.0,
                        dash_duration_ms=1500,
                        melee_width=55,
                        melee_height=55,
                        melee_color=(255, 0, 0),
                        damage=115,
                        cooldown_ms=0,
                        state=state
                    )

                    # APPLY DAMAGE TO PLAYER IF HIT
                    if self.target_player.melee_hitbox.colliderect(self.melee_hitbox):
                        self.target_player.shield_system.take_damage(self.touch_damage)
                        self.target_player.on_hit()
                        print("player hit")
                        self._melee_active = False
                        self._melee_last_time = now

            # ─────────────────────────────
            # CONTINUE MELEE (NO RETARGET)
            # ─────────────────────────────
            elif self._melee_active:
                self.melee_strike(
                    dash_speed=4.0,
                    dash_duration_ms=2000,
                    melee_width=55,
                    melee_height=55,
                    melee_color=(255, 0, 0),
                    damage=115,
                    cooldown_ms=0,
                    state=state
                )

                # APPLY DAMAGE TO PLAYER IF HIT
                if self.target_player.melee_hitbox.colliderect(self.melee_hitbox):
                    self.target_player.shield_system.take_damage(self.touch_damage)
                    self.target_player.on_hit()
                    print("player hit")
                    self._melee_active = False
                    self._melee_last_time = now
        self.check_rope_collision(self.target_player)




    # -------------------------------------------------
    # TOUCH DAMAGE (STANDALONE FUNCTION)
    # -------------------------------------------------

    # -------------------------------------------------
    # MOVEMENT
    # -------------------------------------------------
    def phase_two_move_ai(self, player) -> None:
        if player is None:
            return

        # enemy center
        ex = self.x + self.width / 2
        ey = self.y + self.height / 2

        # player center
        px = player.x + player.width / 2
        py = player.y + player.height / 2

        dx = px - ex
        dy = py - ey
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        # normalize
        dx /= dist
        dy /= dist

        # move toward player using enemy move speed
        self.x += dx * self.moveSpeed
        self.y += dy * self.moveSpeed

        self.update_hitbox()

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
