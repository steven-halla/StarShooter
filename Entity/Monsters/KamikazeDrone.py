import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class KamikazeDrone(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement
        self.mover: MoveRectangle = MoveRectangle()
        self.move_direction: int = random.choice([-1, 1])
        self.speed: float = 1.5

        self.edge_padding: int = 0

        # identity / visuals
        self.name: str = "kamikaze_drone"
        self.width: int = 40
        self.height: int = 40
        self.color = GlobalConstants.RED

        self.kamikaze_drone_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.kamikaze_drone_image

        # stats
        self.enemyHealth: float = 5.0
        self.maxHealth: float = 5.0
        self.exp: int = 1
        self.credits: int = 5

        # ranged attack
        self.bulletColor = GlobalConstants.SKYBLUE
        self.attack_timer = Timer(3.0)

        # touch damage
        # touch / explosion damage
        self.touch_damage: int = 70
        self.touch_timer = Timer(0.75)

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
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

        # direction vector toward player
        px = self.target_player.x
        py = self.target_player.y

        dx = px - self.x
        dy = py - self.y
        dist = max(1, (dx * dx + dy * dy) ** 0.5)

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

        self.update_hitbox()

        # explosion check
        if self.hitbox.colliderect(self.target_player.hitbox):
            self.on_hit_player(state)
    # -------------------------------------------------
    # TOUCH DAMAGE (STANDALONE FUNCTION)
    # -------------------------------------------------

    # -------------------------------------------------


    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------


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

    def clamp_vertical(self) -> None:
        pass

    def on_hit_player(self, state):

        """Handle drone impact damage (player or non-player target)."""
        if self.target_player is None:
            return

        if not hasattr(self.target_player, "shipHealth"):
            return

        damage = self.touch_damage

        # ----------------------------
        # SHIELD SYSTEM FIRST (ONE PATH)
        # ----------------------------
        remaining_damage = 0

        if hasattr(self.target_player, "shield_system") and self.target_player.shield_system is not None:
            result = self.target_player.shield_system.take_damage(damage)

            # If your shield_system.take_damage returns spillover damage, use it.
            if isinstance(result, (int, float)):
                remaining_damage = result
            else:
                remaining_damage = 0
        else:
            remaining_damage = damage

        # ----------------------------
        # HP ONLY GETS HIT BY SPILLOVER
        # ----------------------------
        if remaining_damage > 0:
            self.target_player.shipHealth -= remaining_damage

        # ----------------------------
        # HIT REACTION ONCE
        # ----------------------------
        if hasattr(self.target_player, "on_hit"):
            self.target_player.on_hit()

        # ==============================
        # NON-PLAYER TARGET (Station)
        # ==============================
        elif hasattr(self.target_player, "hp"):
            self.target_player.hp -= self.explosion_damage

        self.enemyHealth = 0  # mark for removal
