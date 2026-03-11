import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class BileSpitter(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement
        self.mover: MoveRectangle = MoveRectangle()
        self.move_direction: int = random.choice([-1, 1])
        self.moveSpeed: float = 2.0
        self.edge_padding: int = 0

        # identity / visuals
        self.name: str = "BileSpitter"
        self.width: int = 172
        self.height: int = 140
        self.color = GlobalConstants.RED

        self.bile_spitter_image = pygame.image.load(
            "Assets/Tyler Favorites Pack/1st 50/200 Mid/Earth King.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image

        # stats
        self.enemyHealth: float = 2.0
        self.maxHealth: float = 2.0
        self.exp: int = 1
        self.credits: int = 5

        # ranged attack
        self.bulletColor = GlobalConstants.SKYBLUE
        self.attack_timer = Timer(3.0)

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


        self.update_hitbox()



        if state.starship.current_level != 3:
            if self.is_active and self.attack_timer.is_ready():
                self.shoot_single_bullet_aimed_at_player(
                    bullet_speed=3.2,
                    bullet_width=18,
                    bullet_height=18,
                    bullet_color=self.bulletColor,
                    bullet_damage=30,
                    state=state
                )
                self.attack_timer.reset()

        else:
            if self.is_active and self.attack_timer.is_ready():
                self.shoot_single_bullet_aimed_at_player(
                    bullet_speed=1.8,
                    bullet_width=20,
                    bullet_height=20,
                    bullet_color=self.bulletColor,
                    bullet_damage=40,
                    state=state
                )
                self.attack_timer.reset()

        # 🔑 CALL TOUCH DAMAGE HANDLER
        self.player_collide_damage(state.starship)
        self.moveAI()


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
        # self.draw_bomb(surface, self.camera)

        super().draw(surface, camera)

        # print(f"DEBUG BossLevelOne.draw: is_active={self.is_active} x={self.x} y={self.y} width={self.width} height={self.height}")

        scale = camera.zoom

        if not self.is_active:
            # Check why it might not be active
            player_in_vicinity = self.player_in_vicinity()
            is_on_screen = self.mover.enemy_on_screen(self, camera)
            # print(f"DEBUG BossLevelOne.draw: is_active is False. player_in_vicinity={player_in_vicinity}, is_on_screen={is_on_screen}")
            # return # Temporarily comment out to force drawing for debug
            # pass # Keep it for now to avoid empty block

        # print(f"DEBUG BossLevelOne.draw: RENDERING at {self.x}, {self.y} size {self.width}x{self.height}")

        # Ensure we have valid dimensions to avoid scale errors
        draw_width = max(1, int(self.width * scale))
        draw_height = max(1, int(self.height * scale))

        # Frame size is 320x150 (sheet is 1280x600, 4x4 grid)
        # Using first frame (top-left)
        sprite_rect = pygame.Rect(0, 0, 246, 160)
        sprite = self.enemy_image.subsurface(sprite_rect)

        scaled_sprite = pygame.transform.scale(
            sprite,
            (draw_width, draw_height)
        )

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)
        # print(f"DEBUG BossLevelOne.draw: screen_x={screen_x} screen_y={screen_y}")
        surface.blit(scaled_sprite, (screen_x, screen_y))
    # def draw(self, surface: pygame.Surface, camera):
    #     if not self.is_active:
    #         return
    #
    #     super().draw(surface, camera)
    #
    #     scale = camera.zoom
    #     scaled_sprite = pygame.transform.scale(
    #         self.bile_spitter_image,
    #         (int(self.width * scale), int(self.height * scale))
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
