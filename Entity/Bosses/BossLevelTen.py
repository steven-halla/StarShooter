import random
import pygame
from pygame import surface

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Entity.Monsters.RescuePod import RescuePod
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelTen(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.name: str = "BossLevelTen"
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20
        self.fire_interval_ms: int = 2000
        self.last_shot_time: int = 0
        self.speed: float = 0.4
        self.enemyHealth: float = 1111.0
        self.maxHealth: float = 1111.0
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
        self.aimed_shot_timer = Timer(1.0)  # 1 second

        self.phase_1 = True
        self.phase_2 = False
        self.phase_3 = False

    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return
        ####DO NOT REMOVE THIS YOU MOTHER FUCKER
        # hp_pct = (self.enemyHealth / self.maxHealth) * 100 if self.maxHealth else 0
        #
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
        ###### DO NOT REMOVE THIS YOU MOTHER FUCKER
        self.moveAI()

        # WORLD-SPACE hitbox
        self.update_hitbox()




        now = pygame.time.get_ticks()


    def moveAI(self) -> None:
        if self.phase_1:
            # move left/right only, clamp to screen bounds (WORLD X because camera.x is fixed at 0)
            window_width = GlobalConstants.BASE_WINDOW_WIDTH

            if not hasattr(self, "_last_x"):
                self._last_x = self.x

            if self.move_direction > 0:
                self.mover.enemy_move_right(self)
            else:
                self.mover.enemy_move_left(self)

            # Check boundaries and switch direction
            if self.x <= self.edge_padding:
                self.x = self.edge_padding
                self.move_direction = 1
            elif self.x + self.width >= (self.camera.window_width / self.camera.zoom) - self.edge_padding:
                self.x = (self.camera.window_width / self.camera.zoom) - self.edge_padding - self.width
                self.move_direction = -1

            # Fallback if stuck (e.g. by clamp_horizontal)
            if self.x == self._last_x:
                self.move_direction *= -1

            self._last_x = self.x

        elif self.phase_2:
            pass

        elif self.phase_3:
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

        ###### DO NOT REMOVE The below YOU MOTHER FUCKER these are
        ###### important instructions for this task

#phase 1
# rain - balls shoot up and then down on player, moves enemy left/right
#phase 2
# boomerrange - fires two bullets that travel to player and then back to enemy
#figure 8 attack meellee attack at player
#phase 3 go to center of screen and aim at player
# flame thrower - go center of screen and aim flame thrower at player
#missiles - shoots missiles that target player
