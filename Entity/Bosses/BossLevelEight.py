import random
import pygame
from pygame import surface

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Entity.Monsters.RescuePod import RescuePod
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelEight(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.name: str = "BossLevelEight"
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED

        self.speed: float = 0.4
        self.enemyHealth: float = 2000.0
        self.maxHealth: float = 2000.0

        # No longer using self.enemyBullets - using game_state.enemy_bullets instead
        self.moveSpeed: float = 2.2
        self.phase_1: bool = True
        self.phase_2: bool = False
        self.phase_3: bool = False
        # --- Wave beam timers---
        self.wave_beam_timer = Timer(1.0)
        # Offset to fire immediately
        self.wave_beam_timer.last_time_ms -= self.wave_beam_timer.interval_ms
        # splatter cannnon timers
        self.splatter_cannon_timer = Timer(5.0)
        # Offset to fire immediately
        self.splatter_cannon_timer.last_time_ms -= self.splatter_cannon_timer.interval_ms

        self.splatter_cannon_sequence_timer = Timer(0.9)
        # Offset to fire immediately
        self.splatter_cannon_sequence_timer.last_time_ms -= self.splatter_cannon_sequence_timer.interval_ms

        self.splatter_cannon_sequence_counter = 0

        # __init__ snippet (Boss / Enemy that will fire acid missiles)

        self.acid_missiles_timer = Timer(5.0)  # fire every 5 seconds
        # fire immediately (optional)
        self.acid_missiles_timer.last_time_ms -= self.acid_missiles_timer.interval_ms


        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image
        self.touch_damage: int = 10
        # state machine

    def update(self, state) -> None:
        super().update(state)

        # -------------------------
        # PHASE SELECT (by HP %)
        # -------------------------
        hp_pct = (self.enemyHealth / self.maxHealth) * 100 if self.maxHealth else 0

        # if hp_pct > 70:
        #     self.phase_1 = True
        #     self.phase_2 = False
        #     self.phase_3 = False
        # elif hp_pct > 40:
        #     self.phase_1 = False
        #     self.phase_2 = True
        #     self.phase_3 = False
        # else:
        #     self.phase_1 = False
        #     self.phase_2 = False
        #     self.phase_3 = True
        self.phase_2 = True
        self.phase_3 = False
        self.phase_1 = False
        if not self.is_active:
            return

        # movement / hitbox
        self.moveAI()
        self.update_hitbox()



        # -------------------------
        # PHASE BEHAVIOR HOOKS
        # -------------------------
        if self.phase_1:
            # update snippet (drop where attacks run, after is_active check)
            if self.splatter_cannon_timer.is_ready():
                if self.splatter_cannon_sequence_timer.is_ready():
                    self.splatter_cannon(
                        bullet_speed=1.7,
                        bullet_width=5,
                        bullet_height=5,
                        bullet_color=self.bulletColor,
                        bullet_damage=5,
                        low_rand_range=-0.20,
                        high_rand_range=0.99,
                        bullet_count=15,
                        state=state
                    )
                    self.splatter_cannon_sequence_timer.reset()
                    self.splatter_cannon_sequence_counter += 1

                    if self.splatter_cannon_sequence_counter >= 3:
                        self.splatter_cannon_timer.reset()
                        self.splatter_cannon_sequence_counter = 0
            # -------------------------
            # WAVE BEAM (every 5 seconds)
            # -------------------------
            if self.wave_beam_timer.is_ready():
                # example: fire horizontal (waves up/down)
                self.wave_beam(
                    state=state,
                    direction="down",  # "left"/"right" => wave on Y, "up"/"down" => wave on X
                    attack_power=25,
                    speed=3.0,
                    wave_range=30.0,
                    wave_speed=0.02,
                    rof_ms=0,  # single beam shot when timer hits (no extra ROF gating)
                    width=60,
                    height=12,
                    bullet_color=self.bulletColor,
                )
                self.wave_beam_timer.reset()
        elif self.phase_2:
            if self.acid_missiles_timer.is_ready():
                self.acid_missiles(
                    state=state,
                    speed=3.5,
                    height=18,
                    width=18,
                    power=20,
                    life=1,
                    max_life=1,
                    number=3
                )
                self.acid_missiles_timer.reset()
        elif self.phase_3:
            pass

    def moveAI(self) -> None:
        # -------------------------
        # PHASE STATE MACHINE
        # -------------------------

        if self.phase_1:
            # move left/right only, clamp to screen bounds (WORLD X because camera.x is fixed at 0)
            if not hasattr(self, "_p1_dir"):
                self._p1_dir = 1  # 1 = right, -1 = left

            self.x += self.moveSpeed * self._p1_dir

            # clamp to visible world width (camera doesn't scroll X)
            max_x = (self.camera.window_width / self.camera.zoom) - self.width

            if self.x < 0:
                self.x = 0
                self._p1_dir = 1
            elif self.x > max_x:
                self.x = max_x
                self._p1_dir = -1

        elif self.phase_2:
            # do phase 2 behavior here
            # when you're ready to switch:
            # self.phase_2 = False
            # self.phase_3 = True
            pass

        elif self.phase_3:
            # do phase 3 behavior here
            pass

    def draw(self, surface: pygame.Surface, camera):
        # self.draw_bomb(surface, self.camera)


        super().draw(surface, camera)

        if not self.is_active:
            return
        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.bile_spitter_image.subsurface(sprite_rect)

        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)
        surface.blit(scaled_sprite, (screen_x, screen_y))

    def clamp_vertical(self) -> None:
        pass
