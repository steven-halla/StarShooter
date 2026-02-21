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
        # --- BossLevelEight.__init__ (add this with your other fields) ---
        self.wave_beam_timer = Timer(1.0)
        self.wave_beam_timer.reset()


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

        if hp_pct > 70:
            self.phase_1 = True
            self.phase_2 = False
            self.phase_3 = False
        elif hp_pct > 40:
            self.phase_1 = False
            self.phase_2 = True
            self.phase_3 = False
        else:
            self.phase_1 = False
            self.phase_2 = False
            self.phase_3 = True

        if not self.is_active:
            return

        # movement / hitbox
        self.moveAI()
        self.update_hitbox()



        # -------------------------
        # PHASE BEHAVIOR HOOKS
        # -------------------------
        if self.phase_1:
            # -------------------------
            # WAVE BEAM (every 5 seconds)
            # -------------------------
            if self.wave_beam_timer.is_ready():
                # example: fire horizontal (waves up/down)
                self.wave_beam(
                    state=state,
                    direction="down",  # "left"/"right" => wave on Y, "up"/"down" => wave on X
                    attack_power=25,
                    speed=5.0,
                    wave_range=30.0,
                    wave_speed=0.02,
                    rof_ms=0,  # single beam shot when timer hits (no extra ROF gating)
                    width=60,
                    height=12,
                    bullet_color=self.bulletColor,
                )
                self.wave_beam_timer.reset()
        elif self.phase_2:
            pass
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
