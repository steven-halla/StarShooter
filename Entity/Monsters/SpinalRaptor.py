import pygame
import random

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class SpinalRaptor(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement helper
        self.mover: MoveRectangle = MoveRectangle()
        self.camera = None

        # appearance
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED

        # movement stats
        self.speed: float = .9

        # gameplay stats
        self.enemyHealth: int = 10
        self.exp: int = 1
        self.credits: int = 5

        # kamikaze-specific
        self.target_player = None     # will be assigned externally
        self.rescue_pod_group = None  # will be assigned externally
        self.is_exploding = False     # state toggle for explosion
        self.explosion_damage: int = 20  # huge damage on hit

        self.kamikaze_drone_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.kamikaze_drone_image  # 🔑 REQUIRED

        self.is_on_screen = False

    def update(self):
        super().update()

        self.update_hitbox()

        # check if visible first
        self.is_on_screen = self.mover.enemy_on_screen(self, self.camera)

        # do NOT track if drone is not yet visible
        if not self.is_on_screen:
            return

        if self.target_player is None:
            return

        # Check if there are any rescue pods on screen to target
        target_x = self.target_player.x
        target_y = self.target_player.y

        # Default to targeting player
        target_rescue_pod = False

        # If we have access to rescue pods, check if any are on screen
        if self.rescue_pod_group is not None and len(self.rescue_pod_group) > 0:
            for pod in self.rescue_pod_group:
                # Check if pod is on screen
                if self.mover.enemy_on_screen(pod, self.camera):
                    # Found a rescue pod on screen, target it instead of player
                    target_x = pod.x
                    target_y = pod.y
                    target_rescue_pod = True
                    break

        # If no rescue pods on screen, target player (already set as default)

        # Calculate direction vector toward target (either rescue pod or player)
        dx = target_x - self.x
        dy = target_y - self.y
        dist = max(1, (dx * dx + dy * dy) ** 0.5)

        # Implement pounce move: triple speed when 100 pixels from target
        current_speed = self.speed
        if dist <= 100:
            print("raptor nomming time")
            # Pounce! Triple the speed when close to target
            current_speed = self.speed * 3

        self.x += (dx / dist) * current_speed
        self.y += (dy / dist) * current_speed

        self.update_hitbox()




    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)  # 🔑 REQUIRED

        sprite_rect = pygame.Rect(10, 425, 32, 32)
        sprite = self.kamikaze_drone_image.subsurface(sprite_rect)

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
