import pygame
import random
import math

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class RectangleAttack:
    def __init__(self, start_x, start_y, target_x, target_y, width=20, height=10, speed=5.0, damage=15):
        # Position
        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y

        # Size
        self.width = width
        self.height = height

        # Damage
        self.damage = damage

        # Direction
        dx = target_x - start_x
        dy = target_y - start_y
        dist = max(1, math.hypot(dx, dy))
        self.dx = (dx / dist) * speed
        self.dy = (dy / dist) * speed

        # Hitbox
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

        # State
        self.is_active = True

    def update(self):
        if not self.is_active:
            return

        self.x += self.dx
        self.y += self.dy

        # Update hitbox
        self.hitbox.x = self.x
        self.hitbox.y = self.y

    def draw(self, surface, camera):
        if not self.is_active:
            return

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        rect_width = int(self.width * camera.zoom)
        rect_height = int(self.height * camera.zoom)

        pygame.draw.rect(surface, (255, 0, 0), (screen_x, screen_y, rect_width, rect_height))


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

        # Pounce and freeze mechanics
        self.has_pounced = False
        self.post_pounce_timer = Timer(3)  # 3-second timer after pouncing
        self.freeze_timer = Timer(3)       # 3-second freeze duration
        self.is_frozen = False             # Flag to indicate if raptor is frozen

        # Player damage tracking
        self.has_damaged_player = False    # Flag to track if raptor has damaged player

        # Rectangle attack mechanics
        self.rectangle_attacks = []
        self.rectangle_attack_timer = Timer(10)  # 10-second cooldown between attacks
        self.rectangle_attack_distance = 150  # Distance in feet to trigger attack

    def shoot_rectangle(self):
        """Shoot a rectangle attack at the player"""
        if self.target_player is None:
            return

        # Get the center positions
        start_x = self.x + self.width / 2
        start_y = self.y + self.height / 2

        target_x = self.target_player.x + self.target_player.width / 2
        target_y = self.target_player.y + self.target_player.height / 2

        # Create the rectangle attack
        rect_attack = RectangleAttack(
            start_x=start_x,
            start_y=start_y,
            target_x=target_x,
            target_y=target_y
        )

        # Add to the list of active rectangle attacks
        self.rectangle_attacks.append(rect_attack)

        # Reset the timer
        self.rectangle_attack_timer.reset()

        # print("SpinalRaptor shot a rectangle attack!")

    def update(self, state):
        super().update(state)

        self.update_hitbox()

        # check if visible first
        self.is_on_screen = self.mover.enemy_on_screen(self, self.camera)

        # do NOT track if drone is not yet visible
        if not self.is_on_screen:
            return

        if self.target_player is None:
            return

        # Update all active rectangle attacks
        # for attack in list(self.rectangle_attacks):
        #     attack.update()
        #
        #     # Check if the attack hit the player
        #     if attack.is_active and attack.hitbox.colliderect(self.target_player.hitbox):
        #         # Apply damage to player
        #         if hasattr(self.target_player, "take_damage"):
        #             self.target_player.take_damage(attack.damage)
        #         # Deactivate the attack
        #         attack.is_active = False
        #         # print("Rectangle attack hit player!")
        #
        #     # Remove inactive attacks
        #     if not attack.is_active:
        #         self.rectangle_attacks.remove(attack)
        #
        # # Check for collision with player
        # if self.target_player and not self.has_damaged_player:
        #     player_rect = self.target_player.hitbox
        #     if self.hitbox.colliderect(player_rect):
        #         # Raptor has collided with player, set flag and freeze
        #         self.has_damaged_player = True
        #         self.is_frozen = True
        #         self.freeze_timer.reset()
        #         # print("raptor hit player, freezing for 3 seconds")
        #         return  # Don't move after hitting player
        #
        # # Handle freeze state
        # if self.is_frozen:
        #     # Check if freeze period is over
        #     if self.freeze_timer.is_ready():
        #         self.is_frozen = False
        #         self.has_pounced = False  # Reset pounce flag to allow pouncing again
        #         self.has_damaged_player = False  # Reset damage flag to allow freezing again
        #         # print("raptor unfrozen, can pounce again")
        #     return  # Don't move while frozen
        #
        # # Handle post-pounce timer
        # if self.has_pounced and not self.is_frozen:
        #     if self.post_pounce_timer.is_ready():
        #         # After 3 seconds, freeze the raptor
        #         self.is_frozen = True
        #         self.freeze_timer.reset()
        #         # print("raptor frozen")
        #         return  # Don't move when just frozen
        #
        # # Check if there are any rescue pods on screen to target
        # target_x = self.target_player.x
        # target_y = self.target_player.y
        #
        # # Default to targeting player
        # target_rescue_pod = False
        #
        # # If we have access to rescue pods, check if any are on screen
        # if self.rescue_pod_group is not None and len(self.rescue_pod_group) > 0:
        #     for pod in self.rescue_pod_group:
        #         # Check if pod is on screen
        #         if self.mover.enemy_on_screen(pod, self.camera):
        #             # Found a rescue pod on screen, target it instead of player
        #             target_x = pod.x
        #             target_y = pod.y
        #             target_rescue_pod = True
        #             break
        #
        # # If no rescue pods on screen, target player (already set as default)
        #
        # # Calculate direction vector toward target (either rescue pod or player)
        # dx = target_x - self.x
        # dy = target_y - self.y
        # dist = max(1, (dx * dx + dy * dy) ** 0.5)
        #
        # # Check if player is within rectangle attack range (150 feet) and timer is ready
        # if dist <= self.rectangle_attack_distance and self.rectangle_attack_timer.is_ready() and not target_rescue_pod:
        #     self.shoot_rectangle()
        #
        # # Implement pounce move: triple speed when 100 pixels from target
        # current_speed = self.speed
        # if dist <= 100 and not self.has_pounced:
        #     # print("raptor nomming time")
        #     # Pounce! Triple the speed when close to target
        #     current_speed = self.speed * 3
        #     # Set pounce flag and start the post-pounce timer
        #     self.has_pounced = True
        #     self.post_pounce_timer.reset()
        #     # print("raptor pounced, timer started")
        # elif self.has_pounced and not self.is_frozen:
        #     # Continue using triple speed during the post-pounce period
        #     current_speed = self.speed * 3
        #     # print("raptor still in pounce mode")
        #
        # self.x += (dx / dist) * current_speed
        # self.y += (dy / dist) * current_speed
        #
        # self.update_hitbox()




    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)  # 🔑 REQUIRED

        # Draw all active rectangle attacks
        for attack in self.rectangle_attacks:
            attack.draw(surface, camera)

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
