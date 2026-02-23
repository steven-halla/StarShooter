import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class FireLauncher(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement
        self.mover: MoveRectangle = MoveRectangle()
        self.move_direction: int = random.choice([-1, 1])
        self.moveSpeed: float = 2.2
        self.edge_padding: int = 0
        self.is_retreating = False

        # identity / visuals
        self.name: str = "FireLauncher"
        self.width: int = 40
        self.height: int = 40
        self.color = GlobalConstants.RED

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image

        # stats
        self.enemyHealth: float = 10.0
        self.maxHealth: float = 10.0
        self.exp: int = 1
        self.credits: int = 5

        # ranged attack
        self.bulletColor = GlobalConstants.SKYBLUE
        self.attack_timer = Timer(4.0)

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

        # match BileSpitter ordering
        self.update_hitbox()

        # self.moveAI()

        if self.attack_timer.is_ready():
            self.shoot_spores(
                bullet_speed=1.5,
                bullet_width=5,
                bullet_height=5,
                bullet_color=self.bulletColor,
                bullet_damage=20,
                state=state
            )
            self.attack_timer.reset()

        # 🔑 DO NOT REMOVE
        self.player_collide_damage(state.starship)

    # -------------------------------------------------
    # MOVEMENT
    # -------------------------------------------------
    def moveAI(self) -> None:
        if not self.mover.enemy_on_screen(self, self.camera):
            return

        # -------------------------
        # camera bounds (world space)
        # -------------------------
        cam_top = self.camera.y
        cam_bottom = (
                self.camera.y
                + (self.camera.window_height / self.camera.zoom)
                - self.height
        )

        now = pygame.time.get_ticks()

        # -------------------------
        # build 3 stored variations ONCE
        # each variation = (up_ms, down_ms) totaling 5000ms
        # up is always 1–2 seconds, down is the remainder (3–4 seconds)
        # -------------------------
        if not hasattr(self, "y_move_variations"):
            self.y_move_variations = []
            for _ in range(3):
                up_ms = random.randint(1000, 2000)
                down_ms = 5000 - up_ms
                self.y_move_variations.append((up_ms, down_ms))

            # start first sequence
            self.y_sequence_start_ms = now
            self.y_active_variation = random.choice(self.y_move_variations)

        # -------------------------
        # start a new 5-second sequence when the current one ends
        # pick randomly from the 3 stored variations
        # -------------------------
        elapsed = now - self.y_sequence_start_ms
        if elapsed >= 5000:
            self.y_sequence_start_ms = now
            self.y_active_variation = random.choice(self.y_move_variations)
            elapsed = 0

        up_ms, down_ms = self.y_active_variation  # down_ms exists for clarity

        # -------------------------
        # decide direction for this moment in the 5s sequence
        # first: up for 1–2s
        # then: down for the remaining 3–4s
        # -------------------------
        move_up_now = (elapsed < up_ms)

        # never move UP if near top within 50px
        top_block_line = cam_top + 50
        if move_up_now and self.y <= top_block_line:
            move_up_now = False  # force down smoothly (no snapping)

        # -------------------------
        # movement
        # -------------------------
        if move_up_now:
            self.mover.enemy_move_up(self)
        else:
            self.mover.enemy_move_down(self)

        # -------------------------
        # clamp after moving (prevents leaving the screen)
        # -------------------------
        if self.y < cam_top:
            self.y = cam_top
        elif self.y > cam_bottom:
            self.y = cam_bottom
    # def moveAI(self) -> None:
    #     if not self.mover.enemy_on_screen(self, self.camera):
    #         return
    #
    #     if not hasattr(self, "base_y"):
    #         self.base_y = self.y
    #         self.move_direction_y = 1
    #
    #     screen_bottom_world = (
    #         self.camera.y
    #         + (self.camera.window_height / self.camera.zoom)
    #     )
    #
    #     if (
    #         not self.is_retreating
    #         and self.y + self.height >= screen_bottom_world - 50
    #     ):
    #         self.is_retreating = True
    #         self.retreat_start_y = self.y
    #
    #     if self.is_retreating:
    #         self.mover.enemy_move_up(self)
    #         moved = self.retreat_start_y - self.y
    #
    #         if moved >= 200:
    #             self.is_retreating = False
    #             self.base_y = self.y
    #         return
    #
    #     desired_top = self.base_y - 100
    #     desired_bottom = self.base_y + 100
    #
    #     cam_top = self.camera.y
    #     cam_bottom = (
    #         self.camera.y
    #         + (self.camera.window_height / self.camera.zoom)
    #         - self.height
    #     )
    #
    #     patrol_top = max(desired_top, cam_top)
    #     patrol_bottom = min(desired_bottom, cam_bottom)
    #
    #     if self.move_direction_y > 0:
    #         self.mover.enemy_move_down(self)
    #     else:
    #         self.mover.enemy_move_up(self)
    #
    #     if self.y <= patrol_top:
    #         self.y = patrol_top
    #         self.move_direction_y = 1
    #     elif self.y >= patrol_bottom:
    #         self.y = patrol_bottom
    #         self.move_direction_y = -1

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------
    def draw(self, surface: pygame.Surface, camera):
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

        surface.blit(
            scaled_sprite,
            (
                camera.world_to_screen_x(self.x),
                camera.world_to_screen_y(self.y),
            )
        )
    def clamp_vertical(self) -> None:
        pass
