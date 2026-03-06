import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class WaspStinger(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement
        self.mover: MoveRectangle = MoveRectangle()
        self.camera = None
        self.target_player = None
        self.speed: float = 1.0
        self.edge_padding: int = 0

        # identity / visuals
        self.name: str = "WaspStinger"
        self.width: int = 40
        self.height: int = 40
        self.color = GlobalConstants.RED

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
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
        self.spear_timer = Timer(5.0)

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

        # check if visible first
        self.is_on_screen = self.mover.enemy_on_screen(self, self.camera)

        # do NOT track if drone is not yet visible
        if not self.is_on_screen:
            return

        if self.target_player is None:
            return

        # direction vector toward player
        px = self.target_player.x
        py = self.target_player.y

        dx = px - self.x
        dy = py - self.y
        dist = max(1, (dx * dx + dy * dy) ** 0.5)

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

        # 🔑 SPEAR LANCE ATTACK (Triggered when distance <= 100)
        if dist <= 100:
            if self.spear_timer.is_ready():
                self.spear_lance(
                    bullet_width=10,
                    bullet_height=80,  # "Length" is 80 (since it's rooted, 40 might be too short)
                    bullet_color=GlobalConstants.ORANGE,
                    bullet_damage=20,
                    duration=1.0,  # Stay out for 1 second
                    state=state
                )
                self.spear_timer.reset()

        # Update rooted attacks
        self.update_spear_lance()

        self.update_hitbox()

        # 🔑 CALL TOUCH DAMAGE HANDLER
        self.player_collide_damage(state.starship)


    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------
    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)  # 🔑 REQUIRED

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

