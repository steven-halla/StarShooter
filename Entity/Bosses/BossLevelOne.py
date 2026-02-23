import random
import pygame
from pygame import surface

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Entity.Monsters.RescuePod import RescuePod
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelOne(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.name: str = "BossLevelOne"
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20
        self.fire_interval_ms: int = 2000
        self.last_shot_time: int = 0
        self.speed: float = 0.4
        self.enemyHealth: float = 100.0
        self.maxHealth: float = 100.0
        self.exp: int = 1
        self.credits: int = 5
        # No longer using self.enemyBullets - using game_state.enemy_bullets instead
        self.moveSpeed: float = 2.4
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

    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return
        self.moveAI()

        # WORLD-SPACE hitbox
        self.update_hitbox()

        # Always update the blade position in every frame
            # update

        # -------------------------
        # FIRE / REST STATE MACHINE
        # -------------------------

        if self.is_firing:
            # FIRE PHASE
            if self.machine_gun_timer.is_ready():
                self.shoot_multiple_down_vertical_y(
                    bullet_speed=3.7,
                    bullet_width=3,
                    bullet_height=10,
                    bullet_color=self.bulletColor,
                    bullet_damage=10,
                    bullet_count=4,
                    bullet_spread=50,
                    state=state
                )
                self.machine_gun_timer.reset()

            # end FIRE phase → switch to REST
            if self.fire_phase_timer.is_ready():

                self.is_firing = False
                self.rest_phase_timer.reset()

        else:
            # REST PHASE — aimed shot every 1 second
            if self.aimed_shot_timer.is_ready():
                self.shoot_single_bullet_aimed_at_player(
                    bullet_speed=4.0,
                    bullet_width=20,
                    bullet_height=20,
                    bullet_color=self.bulletColor,
                    bullet_damage=50,
                    state=state
                )
                self.aimed_shot_timer.reset()

            # END REST → switch to FIRE
            if self.rest_phase_timer.is_ready():
                self.is_firing = True
                self.fire_phase_timer.reset()
                self.machine_gun_timer.reset()

        now = pygame.time.get_ticks()


        self.last_shot_time = now
        self.player_collide_damage(state.starship)
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
            if self.move_direction > 0:
                self.mover.enemy_move_right(self)
            else:
                self.mover.enemy_move_left(self)



        self._last_x = self.x

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
