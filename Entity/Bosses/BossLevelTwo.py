import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class BossLevelTwo(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement
        self.mover: MoveRectangle = MoveRectangle()
        self.move_direction: int = random.choice([-1, 1])
        self.moveSpeed: float = 1.5
        self.edge_padding: int = 0

        # identity / visuals
        self.name: str = "BossLevelTwo"
        self.width: int = 120
        self.height: int = 120
        self.color = GlobalConstants.RED

        self.bile_spitter_image = pygame.image.load(
            "Assets/Pipoya RPG Monster Pack/non shade/pipo-enemy042b.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image

        # stats
        self.enemyHealth: float = 600.0
        self.maxHealth: float = 600.0
        self.exp: int = 1
        self.credits: int = 5

        # ranged attack
        self.bulletColor = GlobalConstants.SKYBLUE
        self.napalm_attack_timer = Timer(9.7)
        self.splatter_cannon_attack_timer = Timer(4.2)

        # touch damage
        self.touch_damage: int = 10
        self.touch_timer = Timer(0.75)

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
    def update(self, state) -> None:
        super().update(state)

        if not self.is_active:
            return

        self.moveAI()
        self.update_hitbox()

        if self.napalm_attack_timer.is_ready():
            self.shoot_napalm(
                bullet_speed=3.3,
                bullet_width=20,
                bullet_height=20,
                bullet_color=self.bulletColor,
                bullet_damage=40,
                travel_time=0.5,
                explosion_time=5.0,
                aoe_size=(20, 20),
                state=state
            )
            self.splatter_cannon_attack_timer.reset()
            self.napalm_attack_timer.reset()

        if self.splatter_cannon_attack_timer.is_ready():
            self.splatter_cannon(
                bullet_speed=2.2,
                bullet_width=16,
                bullet_height=16,
                bullet_color=self.bulletColor,
                bullet_damage=25,
                low_rand_range=-0.3,
                high_rand_range=0.9,
                bullet_count=7,
                state=state
            )
            self.splatter_cannon_attack_timer.reset()

        # 🔑 CALL TOUCH DAMAGE HANDLER
        self.player_collide_damage(state.starship)

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

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------
    def draw(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        super().draw(surface, camera)

        sprite_rect = pygame.Rect(0, 0, 480, 480)
        sprite = self.enemy_image.subsurface(sprite_rect)

        scale = camera.zoom
        scaled_width = int(self.width * scale)
        scaled_height = int(self.height * scale * 1.50)
        height_offset = scaled_height - int(self.height * scale)

        scaled_sprite = pygame.transform.scale(
            sprite,
            (scaled_width, scaled_height)
        )

        surface.blit(
            scaled_sprite,
            (
                camera.world_to_screen_x(self.x),
                camera.world_to_screen_y(self.y) - height_offset,
            )
        )
    # def draw(self, surface: pygame.Surface, camera):
    #     if not self.is_active:
    #         return
    #
    #     super().draw(surface, camera)
    #
    #     # The image is 480x480, and it's a 4x4 grid.
    #     # Each frame is 120x120.
    #     sprite_rect = pygame.Rect(0, 0, 480, 480)
    #     sprite = self.enemy_image.subsurface(sprite_rect)
    #
    #     scale = camera.zoom
    #     scaled_sprite = pygame.transform.scale(
    #         sprite,
    #         (int(self.width * scale), int(self.height * scale ))
    #     )
    #
    #     surface.blit(
    #         scaled_sprite,
    #         (
    #             camera.world_to_screen_x(self.x),
    #             camera.world_to_screen_y(self.y),
    #         )
    #     )

    def clamp_vertical(self) -> None:
        pass
