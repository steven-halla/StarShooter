import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet

# need to update so it tarets player if worm not on scrreen
class Slaver(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.has_retreat_triggered = False
        self.target_worm = None
        self.has_touched_worm = False   # ✅ ADD THIS


        self.transport_worms: list = []        # -------------------------
        # BILE BURST FIRE
        # -------------------------
        self.bile_burst_count = 0
        self.bile_burst_max = 3
        self.bile_burst_delay_ms = 500
        self.last_bile_shot_time = 0
        self.is_bile_bursting = False

        self.burst_cooldown_ms = 3500
        self.last_burst_time = pygame.time.get_ticks() - self.burst_cooldown_ms
        self.tagged_worms: list | None = None
        # -------------------------
        # ENEMY APPEARANCE
        # -------------------------
        self.width: int = 40
        self.height: int = 40
        self.color = GlobalConstants.RED

        # -------------------------
        # BULLET APPEARANCE
        # -------------------------
        self.bulletColor = GlobalConstants.SKYBLUE
        self.bulletWidth = 20
        self.bulletHeight = 20

        # -------------------------
        # BULLET MOVEMENT
        # -------------------------
        self.bileSpeed = 3

        # -------------------------
        # GAMEPLAY STATS
        # -------------------------
        self.speed: float = 1.2
        self.enemyHealth: int = 150
        self.maxHealth: int = 150
        self.exp: int = 1
        self.credits: int = 5
        self.is_retreating = False
        self.retreat_start_y = None

        self.enemyBullets: list[Bullet] = []

        # -------------------------
        # AI MOVEMENT STATE (DO NOT TOUCH)
        # -------------------------
        self.moveSpeed: float = .5
        self.edge_padding: int = 30
        self.move_direction: int = random.choice([-1, 1])

        self.move_interval_ms: int = 3000
        self.last_move_toggle: int = pygame.time.get_ticks()
        self.is_moving: bool = True

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image  # 🔑 REQUIRED




    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return

        self.update_hitbox()

        # ✅ ACQUIRE TARGET IF NEEDED
        if self.target_worm is None or self.target_worm.enemyHealth <= 0:
            if hasattr(self, 'transport_worms') and self.transport_worms:  # <-- this must be injected by the Level
                print(f"[SLAVER] Looking for target worm among {len(self.transport_worms)} worms")
                self.find_nearest_transport_worm(self.transport_worms)
                if self.target_worm:
                    print(f"[SLAVER] Found target worm at ({self.target_worm.x:.1f}, {self.target_worm.y:.1f})")
                else:
                    print("[SLAVER] No target worm found")

        # ✅ MOVE TOWARD TARGET
        if self.target_worm:
            self.move_toward_target_worm()

        now = pygame.time.get_ticks()

        if (
                not self.is_bile_bursting
                and now - self.last_burst_time >= self.burst_cooldown_ms
        ):
            self.is_bile_bursting = True
            self.bile_burst_count = 0
            self.last_bile_shot_time = now
            self.last_burst_time = now

    def find_nearest_transport_worm(self, worms: list) -> None:
        nearest = None
        nearest_dist = float("inf")

        for worm in worms:
            dx = worm.x - self.x
            dy = worm.y - self.y
            dist_sq = dx * dx + dy * dy

            if dist_sq < nearest_dist:
                nearest_dist = dist_sq
                nearest = worm

        self.target_worm = nearest

    def move_toward_target_worm(self) -> None:

        if self.target_worm is None:
            return

        dx = self.target_worm.x - self.x
        dy = self.target_worm.y - self.y

        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        # Print slaver and worm locations
        if hasattr(self, 'camera'):
            slaver_screen_x = self.camera.world_to_screen_x(self.x)
            slaver_screen_y = self.camera.world_to_screen_y(self.y)
            worm_screen_x = self.camera.world_to_screen_x(self.target_worm.x)
            worm_screen_y = self.camera.world_to_screen_y(self.target_worm.y)
            print(f"[SLAVER] World: ({self.x:.1f}, {self.y:.1f}) Screen: ({slaver_screen_x:.1f}, {slaver_screen_y:.1f})")
            print(f"[WORM] World: ({self.target_worm.x:.1f}, {self.target_worm.y:.1f}) Screen: ({worm_screen_x:.1f}, {worm_screen_y:.1f})")
            print(f"[DISTANCE] {dist:.1f} pixels")

        # normalize
        dx /= dist
        dy /= dist

        self.x += dx * self.speed
        self.y += dy * self.speed
        # ✅ COLLISION CHECK WITH TARGET WORM
        if (
                self.target_worm is not None
                and not self.has_touched_worm
                and self.hitbox.colliderect(self.target_worm.hitbox)
        ):
            # 🔑 ADD WORM TO LEVEL LIST
            if hasattr(self, "touched_worms"):
                if self.target_worm not in self.touched_worms:
                    self.touched_worms.append(self.target_worm)

            self.target_worm.enemyHealth = 0
            self.enemyHealth = 0
            self.is_active = False
            self.has_touched_worm = True
        # if self.target_worm is not None:
        #     if self.hitbox.colliderect(self.target_worm.hitbox):
        #         self.enemy_handshake(self.target_worm)
    # -------------------------
    # AI MOVEMENT (UNCHANGED)
    # -------------------------
    # def moveAI(self) -> None:
    #     if not self.mover.enemy_on_screen(self, self.camera):
    #         return
    #
    #     # One-time init
    #     if not hasattr(self, "base_y"):
    #         self.base_y = self.y
    #         self.move_direction_y = 1
    #
    #     screen_bottom_world = (
    #             self.camera.y
    #             + (self.camera.window_height / self.camera.zoom)
    #     )
    #
    #     # -------------------------
    #     # START RETREAT
    #     # -------------------------
    #     if (
    #             not self.is_retreating
    #             and self.y + self.height >= screen_bottom_world - 50
    #     ):
    #         self.is_retreating = True
    #         self.retreat_start_y = self.y
    #         print(f"[RETREAT START] y={self.y:.2f}")
    #
    #     # -------------------------
    #     # RETREAT MOVEMENT (UP 200px)
    #     # -------------------------
    #     if self.is_retreating:
    #         self.mover.enemy_move_up(self)
    #
    #         moved = self.retreat_start_y - self.y
    #         print(f"[RETREAT MOVE] y={self.y:.2f} moved={moved:.2f}")
    #
    #         # Stop retreat after 200px
    #         if moved >= 200:
    #             self.is_retreating = False
    #             self.base_y = self.y  # reset patrol center
    #             print("[RETREAT END]")
    #         return
    #
    #     # -------------------------
    #     # NORMAL PATROL (UNCHANGED)
    #     # -------------------------
    #     desired_top = self.base_y - 100
    #     desired_bottom = self.base_y + 100
    #
    #     cam_top = self.camera.y
    #     cam_bottom = (
    #             self.camera.y
    #             + (self.camera.window_height / self.camera.zoom)
    #             - self.height
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
    #
    #     # print(f"[AI MOVE] y={self.y:.2f} dir={self.move_direction_y}")

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)  # 🔑 REQUIRED

        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.bile_spitter_image.subsurface(sprite_rect)

        scale = camera.zoom
        sprite = pygame.transform.scale(
            sprite, (int(self.width * scale), int(self.height * scale))
        )

        surface.blit(
            sprite,
            (
                camera.world_to_screen_x(self.x),
                camera.world_to_screen_y(self.y),
            ),
        )

        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)

    def enemy_handshake(self, enemy) -> None:
        value = enemy.__class__.__name__

        match value:
            case "TransportWorm":
                print("Touched TransportWorm")

            case "BileSpitter":
                print("Touched BileSpitter")

            case "KamikazeDrone":
                print("Touched KamikazeDrone")

            case _:
                pass
