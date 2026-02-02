import random
import pygame
from pygame import surface

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Entity.Monsters.RescuePod import RescuePod
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class TriSpitter(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.name: str = "TriSpitter"
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20
        self.fire_interval_ms: int = 2000
        self.last_shot_time: int = 0
        self.speed: float = 0.4
        self.enemyHealth: float = 8.0
        self.maxHealth: float = 8.0

        self.exp: int = 1
        self.credits: int = 5
        # No longer using self.enemyBullets - using game_state.enemy_bullets instead
        self.moveSpeed: float = .2
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

    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return
        self.moveAI()
        # print(self.enemyHealth)

        # WORLD-SPACE hitbox
        self.update_hitbox()

        # Always update the blade position in every frame
            # update
        if self.is_active and self.attack_timer.is_ready():
            self.shoot_multiple_down_vertical_y(
                bullet_speed=4.0,
                bullet_width=10,
                bullet_height=50,
                bullet_color=self.bulletColor,
                bullet_damage=25,
                bullet_count=3,
                bullet_spread=44,
                state = state
            )
            self.attack_timer.reset()

        now = pygame.time.get_ticks()


        self.last_shot_time = now
        self.player_collide_damage(state.starship)

    # -------------------------------------------------
    # TOUCH DAMAGE (STANDALONE FUNCTION)
    # -------------------------------------------------



    def moveAI(self) -> None:
        # 🔼 smooth upward drift (fractional movement)
        self.y -= self.moveSpeed

    def draw(self, surface: pygame.Surface, camera):
        # self.draw_bomb(surface, self.camera)
        if not self.is_active:
            return

        super().draw(surface, camera)

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
