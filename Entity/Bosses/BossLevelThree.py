import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Entity.Monsters.TriSpitter import TriSpitter
from Movement.MoveRectangle import MoveRectangle

#CHANGE BOSS ROPE SEE COMMENTS IN ROPE SDECTION
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
        self.enemyHealth: float = 800.0
        self.maxHealth: float = 800.0
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
        if self.enemyHealth > 700:
            self.phase = 1
        elif self.enemyHealth > 500:
            self.phase = 2
        else:
            self.phase = 3
        # self.phase = 3

        # -------------------------
        # PHASE 1 — ROPE + SHOOT
        # -------------------------
        # SINGLE SHOT DOWN VERTICAL Y SHOULD NOT HAPPEN WHEN ROPE OUT IF PLAYER NOT GRBBED
        if self.phase == 1:
            # rope control (uses your working timing block)
            if not hasattr(self, "_rope_was_active"):
                self._rope_was_active = False
            if not hasattr(self, "_rope_next_allowed_time"):
                self._rope_next_allowed_time = 0
            if not hasattr(self, "_rope_caught_player"):
                self._rope_caught_player = False

            ROPE_DURATION_MS = 3000
            ROPE_COOLDOWN_MS = 4000
            ROPE_CATCH_EXTENSION_MS = 3000  # Add 3 seconds when catching player

            if self._rope is None and now >= self._rope_next_allowed_time:
                self.rope_grab(
                    rope_length=160,
                    rope_width=4,
                    rope_speed=3.0,
                    rope_duration_ms=ROPE_DURATION_MS,
                    rope_color=(180, 180, 180),
                    state=state
                )
                self._rope_caught_player = False  # Reset catch flag

            if self._rope is not None:
                # Check if player just got caught (transition from False to True)
                if self.player_caught and not self._rope_caught_player:
                    self._rope.end_time = now + ROPE_CATCH_EXTENSION_MS  # Extend by 3 seconds from NOW
                    self._rope_caught_player = True  # Mark that we caught them

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
                self._rope_caught_player = False  # Reset for next rope

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

        # ─────────────────────────────
        # PHASE 3 – MELEE STRIKE (4s TIMER)
        # ─────────────────────────────
        if self.phase == 3:
            now = pygame.time.get_ticks()

            if not hasattr(self, "_rush_last_time"):
                self._rush_last_time = now

            # summon every 5 seconds

            if not hasattr(self, "_summon_swarm_last_time"):
                self._summon_swarm_last_time = 0

            if now - self._summon_swarm_last_time >= 12000:
                self.summon_swarm(state)
                self._summon_swarm_last_time = now
                print("yupper")

            # arm rush every 3 seconds
            if now - self._rush_last_time >= 2000 and not hasattr(self, "_rush_active"):
                px = self.target_player.x + self.target_player.width / 2
                py = self.target_player.y + self.target_player.height / 2

                ex = self.x + self.width / 2
                ey = self.y + self.height / 2

                dx = px - ex
                dy = py - ey
                dist = math.hypot(dx, dy)

                if dist != 0:
                    self._rush_dir_x = dx / dist
                    self._rush_dir_y = dy / dist
                    self._rush_active = True
                    self._rush_last_time = now

            # MOVE every frame while rushing
            bounds_rect = pygame.Rect(
                0,  # world left (camera never scrolls X)
                self.camera.y,  # top of camera view (world space)
                self.camera.window_width / self.camera.zoom,
                GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom
            )

            self.rush_attack(self.target_player, bounds_rect)

    def summon_swarm(self, state) -> None:
        for _ in range(4):
            enemy = TriSpitter()

            # 🔑 SCALE DOWN HERE (SPAWN-ONLY)
            scale = 0.6  # 60% size
            enemy.width = int(enemy.width * scale)
            enemy.height = int(enemy.height * scale)

            # spawn near top of screen (WORLD SPACE)
            enemy.x = random.randint(
                int(self.camera.x + 40),
                int(self.camera.x + (GlobalConstants.BASE_WINDOW_WIDTH / self.camera.zoom) - 40)
            )
            enemy.y = self.camera.y

            enemy.camera = self.camera
            enemy.target_player = state.starship
            enemy.is_active = True

            enemy.update_hitbox()
            state.enemies.append(enemy)

        print("🧟 SUMMON SWARM → +4 SMALL TRI SPITTERS")
    # -------------------------------------------------
    # UNIQUE attack
    # -------------------------------------------------

    def rush_attack(self, player, bounds_rect: pygame.Rect) -> None:
        if player is None or not hasattr(self, "_rush_active"):
            return
        RUSH_SPEED = 4.0

            # move
        self.x += self._rush_dir_x * RUSH_SPEED
        self.y += self._rush_dir_y * RUSH_SPEED
        self.update_hitbox()

        # hit player → stop
        if self.hitbox.colliderect(player.hitbox):
            self.stop_rush()
            return

        # ⬇️ THIS IS WHERE IT WAS
        # hit boundary → stop (NO SLIDING)
        if (
                self.hitbox.left <= bounds_rect.left or
                self.hitbox.right >= bounds_rect.right or
                self.hitbox.top <= bounds_rect.top or
                self.hitbox.bottom >= bounds_rect.bottom
        ):
            # snap inside bounds
            self.x = max(bounds_rect.left, min(self.x, bounds_rect.right - self.width))
            self.y = max(bounds_rect.top, min(self.y, bounds_rect.bottom - self.height))
            self.update_hitbox()

            self.stop_rush()
            return



        # ─────────────────────────────
        # STOP CONDITIONS
        # ─────────────────────────────


        # hit player → stop
        # hit player → stop

    def stop_rush(self) -> None:
        if hasattr(self, "_rush_active"):
            del self._rush_active
        if hasattr(self, "_rush_dir_x"):
            del self._rush_dir_x
        if hasattr(self, "_rush_dir_y"):
            del self._rush_dir_y

        # 🔑 reset cooldown so it doesn't instantly re-arm
        self._rush_last_time = pygame.time.get_ticks()
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


