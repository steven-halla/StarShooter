
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class BossLevelFour(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.name: str = "BossLevelFour"
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20
        self.fire_interval_ms: int = 4000
        self.last_shot_time: int = 0
        self.speed: float = 0.4
        self.enemyHealth: float = 250.0
        self.maxHealth: float = 250.0
        self.exp: int = 1
        self.credits: int = 5
        # No longer using self.enemyBullets - using game_state.enemy_bullets instead
        self.moveSpeed: float = 2.2
        self.edge_padding: int = 0
        self.move_direction: int = random.choice([-1, 1])
        self.move_interval_ms: int = 3000
        self.last_move_toggle: int = pygame.time.get_ticks()
        self.is_moving: bool = True
        # __init__
        self.attack_timer = Timer(3.0)  # 3 seconds

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image
        self.touch_damage: int = 10
        # state machine
        self.is_firing = False

        self.fire_phase_timer = Timer(5.0)  # how long FIRE lasts
        self.rest_phase_timer = Timer(10.0)  # how long REST lasts
        self.machine_gun_timer = Timer(0.5)  # fire rate during FIRE
        # self.aimed_shot_timer = Timer(5.0)  # 1 second
        self.aimed_shot_timer = Timer(random.uniform(3.0, 6.0))

        self.triple_fire_interval_ms = 3800
        self.last_triple_shot_time = pygame.time.get_ticks()
        #

        self.shield_active: bool = True

        self.max_shield_hp: int = 600
        self.shield_hp: int = self.max_shield_hp

        self.shield_toggle_interval_ms = random.choice((3000, 4000))
        self.last_shield_toggle_time = (
            pygame.time.get_ticks()
            - random.randint(0, self.shield_toggle_interval_ms))

    def update(self, state) -> None:
        super().update(state)
        now = pygame.time.get_ticks()

        if not self.is_active:
            return

        # -------------------------------------------------
        # RANDOM PATTERN EVERY 10 SECONDS
        # -------------------------------------------------
        if not hasattr(self, "pattern_last_time"):
            self.pattern_last_time = now

        if now - self.pattern_last_time >= 10000:
            self.pattern_last_time = now

            pattern = random.choice((
                "lr",
                "ud",
                "ul_lr",
                "ur_ll"
            ))

            if pattern == "lr":
                self.shoot_bullets_left_right(
                    bullet_speed=1.0,
                    bullet_width=5,
                    bullet_height=5,
                    bullet_color=GlobalConstants.RED,
                    bullet_damage=22,
                    cooldown_ms=0,
                    state=state
                )

            elif pattern == "ud":
                self.shoot_bullets_up_down(
                    bullet_speed=1.0,
                    bullet_width=5,
                    bullet_height=5,
                    bullet_color=GlobalConstants.RED,
                    bullet_damage=22,
                    cooldown_ms=0,
                    state=state
                )

            elif pattern == "ul_lr":
                self.shoot_bullets_diag_ul_lr(
                    bullet_speed=1.0,
                    bullet_width=5,
                    bullet_height=5,
                    bullet_color=GlobalConstants.RED,
                    bullet_damage=22,
                    cooldown_ms=0,
                    state=state
                )

            elif pattern == "ur_ll":
                self.shoot_bullets_diag_ur_ll(
                    bullet_speed=1.0,
                    bullet_width=5,
                    bullet_height=5,
                    bullet_color=GlobalConstants.RED,
                    bullet_damage=22,
                    cooldown_ms=0,
                    state=state
                )

        # -------------------------------------------------
        # SHIELD TOGGLE
        # -------------------------------------------------
        if now - self.last_shield_toggle_time >= self.shield_toggle_interval_ms:
            self.shield_active = not self.shield_active
            self.last_shield_toggle_time = now

            if self.shield_active:
                self.shield_hp = self.max_shield_hp
                self.shield_toggle_interval_ms = random.choice((3000, 4000))

        # -------------------------------------------------
        # TRIPLE SHOT WHEN SHIELD DOWN
        # -------------------------------------------------


        # WORLD SPACE HITBOX
        self.update_hitbox()

        # -------------------------------------------------
        # AIMED REST SHOT
        # -------------------------------------------------
        if self.aimed_shot_timer.is_ready():
            self.shoot_single_bullet_aimed_at_player(
                bullet_speed=4.0,
                bullet_width=20,
                bullet_height=20,
                bullet_color=self.bulletColor,
                bullet_damage=10,
                state=state
            )
            self.aimed_shot_timer.reset()

        # -------------------------------------------------
        # REST → FIRE TRANSITION
        # -------------------------------------------------
        if self.rest_phase_timer.is_ready():
            self.is_firing = True
            self.fire_phase_timer.reset()
            self.machine_gun_timer.reset()

        self.last_shot_time = now

        # =====================================================
        # DRAW
        # =====================================================
    def draw(self, surface: pygame.Surface, camera):
        scale = camera.zoom
        rect = pygame.Rect(
            camera.world_to_screen_x(self.x),
            camera.world_to_screen_y(self.y),
            int(self.width * scale),
            int(self.height * scale),
        )

        # 🔵 Shield UP
        # 🟣 Shield DOWN
        color = (0, 120, 255) if self.shield_active else (160, 0, 200)
        pygame.draw.rect(surface, color, rect)

