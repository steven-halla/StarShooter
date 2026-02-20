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
        self.enemyHealth: float = 1111.0
        self.maxHealth: float = 1111.0

        # No longer using self.enemyBullets - using game_state.enemy_bullets instead
        self.moveSpeed: float = 2.2
        self.phase_1: bool = True
        self.phase_2: bool = False
        self.phase_3: bool = False


        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image
        self.touch_damage: int = 10
        # state machine


    def update(self, state) -> None:
        super().update(state)
        # drop this near the top of BossLevelEight.update(), after super().update(state)

        hp_pct = (self.enemyHealth / self.maxHealth) * 100 if self.maxHealth else 0

        if hp_pct > 70:
            self.phase_1 = True
            self.phase_2 = False
            self.phase_3 = False
        elif hp_pct > 40:
            # 40% < hp <= 70%
            self.phase_1 = False
            self.phase_2 = True
            self.phase_3 = False
        else:
            # hp <= 40%
            self.phase_1 = False
            self.phase_2 = False
            self.phase_3 = True
        if not self.is_active:
            return
        self.moveAI()

        # WORLD-SPACE hitbox
        self.update_hitbox()
        # -------------------------
        # PHASE STATE MACHINE
        # -------------------------

        if self.phase_1:
            # do phase 1 behavior here
            # when you're ready to switch:
            # self.phase_1 = False
            # self.phase_2 = True
            pass

        elif self.phase_2:
            # do phase 2 behavior here
            # when you're ready to switch:
            # self.phase_2 = False
            # self.phase_3 = True
            pass

        elif self.phase_3:
            # do phase 3 behavior here
            pass


    def moveAI(self) -> None:
        # -------------------------
        # PHASE STATE MACHINE
        # -------------------------

        if self.phase_1:
            # do phase 1 behavior here
            # when you're ready to switch:
            # self.phase_1 = False
            # self.phase_2 = True
            pass

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
