import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
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
        self.name: str = "Slaver"
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
        self.speed: float = .8
        self.enemyHealth: int = 150
        self.maxHealth: int = 150
        self.exp: int = 1
        self.credits: int = 5
        self.is_retreating = False
        self.retreat_start_y = None
        self.attack_player:bool = False

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
        self.touch_damage: int = 10
        self.touch_timer = Timer(0.75)





    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, state) -> None:
        super().update(state)
        if self.touch_timer.is_ready():
            # self.player_collide_damage(state.starship)
            self.touch_timer.reset()

        if not self.is_active:
            return

        self.update_hitbox()

        # 🔒 TOUCH DAMAGE — USE SAME PATTERN AS BILESPITTER

        now = pygame.time.get_ticks()

        # ======================================
        # ATTACK PLAYER MODE
        # ======================================
        # if self.attack_player:
        #
        #     self.target_worm = None
        #
        #     if (
        #             not self.is_bile_bursting
        #             and now - self.last_burst_time >= self.burst_cooldown_ms
        #     ):
        #         self.is_bile_bursting = True
        #         self.bile_burst_count = 0
        #         self.last_bile_shot_time = now
        #         self.last_burst_time = now
            #
            # if self.is_bile_bursting:
            #
            #     if (
            #             self.bile_burst_count < self.bile_burst_max
            #             and now - self.last_bile_shot_time >= self.bile_burst_delay_ms
            #     ):
            #         self.splatter_cannon(
            #             bullet_speed=3.5,
            #             bullet_width=10,
            #             bullet_height=10,
            #             bullet_color=(255, 50, 50),
            #             bullet_damage=25,
            #             low_rand_range=-0.2,
            #             high_rand_range=0.2,
            #             bullet_count=5,
            #             state=state
            #         )
            #
            #         self.bile_burst_count += 1
            #         self.last_bile_shot_time = now
            #
            #     if self.bile_burst_count >= self.bile_burst_max:
            #         self.is_bile_bursting = False
            #
            # return

        # ======================================
        # WORM TARGET MODE
        # ======================================

        if self.target_worm is None or self.target_worm.enemyHealth <= 0:
            if self.transport_worms:
                self.find_nearest_transport_worm(self.transport_worms)

        if self.target_worm:
            self.move_toward_target_worm()

        # self.player_collide_damage(state.starship)

    def find_nearest_transport_worm(self, worms: list) -> None:
        nearest = None
        nearest_dist = float("inf")

        print("SLAVER:", self.x, self.y)

        for worm in worms:
            dx = worm.x - self.x
            dy = worm.y - self.y
            print("WORM:", worm.x, worm.y, "DIST^2:", dx * dx + dy * dy)


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
