# import pygame
# from Constants.GlobalConstants import GlobalConstants
# from Constants.Timer import Timer
# from Movement.MoveRectangle import MoveRectangle
#
#

import pygame
from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Movement.MoveRectangle import MoveRectangle


class StarShip():
    def __init__(self):
        self.height: int = 16
        self.width: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.BLUE
        self.x: int = 0
        self.y: int = 0
        self.moveStarShip: MoveRectangle = MoveRectangle()
        self.speed: float = 5.0

        # firing stats
        self.bullet_fire_interval_seconds: float = 0.05
        self.bullet_timer: Timer = Timer(self.bullet_fire_interval_seconds)
        self.bullet_spread_offset: int = 30
        self.bullets_per_shot: int = 2
        self.bullet_vertical_spacing: int = 22
        self.bulletDamage: int = 1

        self.hitbox: pygame.Rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height
        )
        self.was_hit: bool = False
        self.shipHealth: int = 50

        self.player_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    def update(self) -> None:
        self.update_hitbox()
        # print(self.shipHealth)

    # def draw(self, surface: "pygame.Surface") -> None:
    #     sprite_rect = pygame.Rect(10, 220, 32, 32)  # Adjust if needed
    #     sprite = self.player_image.subsurface(sprite_rect)
    #     scaled_sprite = pygame.transform.scale(sprite, (16, 16))
    #     sprite_x = self.x - 20
    #     sprite_y = self.y - 10
    #     surface.blit(scaled_sprite, (sprite_x, sprite_y))
    def draw(self, surface: pygame.Surface, camera):
        sprite_rect = pygame.Rect(10, 220, 32, 32)
        sprite = self.player_image.subsurface(sprite_rect)

        # scale ship with zoom
        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        # convert world → screen
        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        # draw ship
        surface.blit(scaled_sprite, (screen_x, screen_y))

        # ================================
        #  DRAW PLAYER HITBOX (DEBUG)
        # ================================
        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)

    def update_hitbox(self) -> None:
        self.hitbox.topleft = (int(self.x), int(self.y))

    def on_hit(self) -> None:
        if not self.was_hit:
            self.was_hit = True
            self.color = GlobalConstants.YELLOW
