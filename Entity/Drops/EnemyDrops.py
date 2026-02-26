import random
import pygame
from Constants.GlobalConstants import GlobalConstants


class EnemyDrop:
    SIZE: int = 16

    DROP_HEALTH: str = "RED"
    DROP_SHIELD: str = "BLUE"
    DROP_MISSILE: str = "YELLOW"
    DROP_KI: str = "SKYBLUE"

    @classmethod
    def from_enemy(cls, enemy) -> "EnemyDrop | None":
        enemy_type = enemy.__class__.__name__
        roll = random.random()  # 0.0 <= roll < 1.
        print(f"your roll is {roll}")
        # -------------------------
        # Bile Spitter
        # 25% chance to drop ANY power up
        # -------------------------
        if enemy_type == "BileSpitter":
            if roll < 0.25:
                drop_type = random.choice([
                    cls.DROP_HEALTH,
                    cls.DROP_SHIELD,
                    cls.DROP_MISSILE,
                    cls.DROP_KI,
                ])
                return cls(enemy.x, enemy.y, drop_type)
            return None

        if enemy_type == "FireLauncher":
            if roll < 0.20:
                drop_type = random.choice([
                    cls.DROP_KI
                ])
                return cls(enemy.x, enemy.y, drop_type)
            return None

        # -------------------------
        # Blade Spinner
        # 10% chance to drop a MISSILE
        # -------------------------
        if enemy_type == "BladeSpinner":
            if roll < 0.15:
                return cls(enemy.x, enemy.y, cls.DROP_MISSILE)
            return None

        # -------------------------
        # Tri Spitter
        # 10% chance to drop SHIELD or HEALTH
        # -------------------------
        if enemy_type == "TriSpitter":
            if roll < 0.10:
                drop_type = random.choice([cls.DROP_KI, cls.DROP_HEALTH])
                return cls(enemy.x, enemy.y, drop_type)
            return None

        # -------------------------
        # Fire Launcher
        # 15% chance to drop KI
        # -------------------------
        if enemy_type == "FireLauncher":
            if roll < 0.15:
                return cls(enemy.x, enemy.y, cls.DROP_KI)
            return None

        # -------------------------
        # Wasp Stinger
        # 5% chance to drop HEALTH
        # -------------------------
        if enemy_type == "WaspStinger":
            if roll < 0.05:
                return cls(enemy.x, enemy.y, cls.DROP_HEALTH)
            return None

        # -------------------------
        # Kamikaze Drone
        # 20% chance to drop SHIELD
        # -------------------------
        if enemy_type == "KamikazeDrone":
            if roll < 0.15:
                return cls(enemy.x, enemy.y, cls.DROP_SHIELD)
            return None

        # default: no drops unless you add more rules
        return None

    def __init__(self, x: float, y: float, drop_type: str):
        self.x: float = float(x)
        self.y: float = float(y)
        self.drop_type: str = drop_type

        if drop_type == self.DROP_HEALTH:
            self.color = GlobalConstants.RED
        elif drop_type == self.DROP_SHIELD:
            self.color = GlobalConstants.BLUE
        elif drop_type == self.DROP_MISSILE:
            self.color = GlobalConstants.YELLOW
        elif drop_type == self.DROP_KI:
            self.color = GlobalConstants.SKYBLUE
        else:
            self.color = GlobalConstants.WHITE

        self.rect: pygame.Rect = pygame.Rect(int(self.x), int(self.y), self.SIZE, self.SIZE)
        self.is_active: bool = True

    def update_rect(self) -> None:
        self.rect.topleft = (int(self.x), int(self.y))

    def apply_effect(self, starship) -> None:
        if self.drop_type == self.DROP_HEALTH:
            starship.shipHealth = min(starship.shipHealth + 25, starship.shipHealthMax)

        elif self.drop_type == self.DROP_SHIELD:
            if hasattr(starship, "shield_system"):
                starship.shield_system.current_shield_points = min(
                    starship.shield_system.current_shield_points + 15,
                    starship.shield_system.max_shield_points,
                )
                if hasattr(starship, "current_shield"):
                    starship.current_shield = int(starship.shield_system.current_shield_points)

        elif self.drop_type == self.DROP_MISSILE:
            starship.missile_current = min(starship.missile_current + 1, starship.missile_max)
            if hasattr(starship, "missile"):
                starship.missile.current_missiles = min(
                    starship.missile.current_missiles + 1,
                    starship.missile.max_missiles,
                )

        elif self.drop_type == self.DROP_KI:
            starship.player_ki = min(starship.player_ki + 15, starship.player_max_ki)

    def update(self, starship, drop_list, camera=None) -> None:
        if not self.is_active:
            return

        self.update_rect()

        if self.rect.colliderect(starship.hitbox):
            self.apply_effect(starship)
            self.is_active = False
            if self in drop_list:
                drop_list.remove(self)

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        if not self.is_active:
            return

        if camera is None:
            pygame.draw.rect(surface, self.color, self.rect)
            return

        screen_x = camera.world_to_screen_x(self.rect.x)
        screen_y = camera.world_to_screen_y(self.rect.y)
        size = int(self.SIZE * camera.zoom)
        pygame.draw.rect(surface, self.color, pygame.Rect(screen_x, screen_y, size, size))
# import pygame
# from Constants.GlobalConstants import GlobalConstants
#
#
# class EnemyDrop:
#     SIZE: int = 16
#
#     DROP_HEALTH: str = "BLUE"
#     DROP_SHIELD: str = "PURPLE"
#     DROP_MISSILE: str = "YELLOW"
#
#     def __init__(self, x: float, y: float, drop_type: str):
#         self.x: float = float(x)
#         self.y: float = float(y)
#         self.drop_type: str = drop_type
#
#         if drop_type == self.DROP_HEALTH:
#             self.color = GlobalConstants.BLUE
#         elif drop_type == self.DROP_SHIELD:
#             self.color = GlobalConstants.PURPLE
#         elif drop_type == self.DROP_MISSILE:
#             self.color = GlobalConstants.YELLOW
#         else:
#             self.color = GlobalConstants.WHITE
#
#         self.rect: pygame.Rect = pygame.Rect(int(self.x), int(self.y), self.SIZE, self.SIZE)
#         self.is_active: bool = True
#
#     def update_rect(self) -> None:
#         self.rect.topleft = (int(self.x), int(self.y))
#
#     def apply_effect(self, starship) -> None:
#         if self.drop_type == self.DROP_HEALTH:
#             starship.shipHealth = min(starship.shipHealth + 25, starship.shipHealthMax)
#
#         elif self.drop_type == self.DROP_SHIELD:
#             if hasattr(starship, "shield_system"):
#                 starship.shield_system.current_shield_points = min(
#                     starship.shield_system.current_shield_points + 10,
#                     starship.shield_system.max_shield_points,
#                 )
#                 if hasattr(starship, "current_shield"):
#                     starship.current_shield = int(starship.shield_system.current_shield_points)
#
#         elif self.drop_type == self.DROP_MISSILE:
#             starship.missile_current = min(starship.missile_current + 1, starship.missile_max)
#             if hasattr(starship, "missile"):
#                 starship.missile.current_missiles = min(
#                     starship.missile.current_missiles + 1,
#                     starship.missile.max_missiles,
#                 )
#
#     def handle_pickup(self, state) -> bool:
#         if not self.is_active:
#             return False
#
#         starship = state.starship
#         # Check collision with starship hitbox.
#         # Ensure we use world coordinates for the check.
#         if self.rect.colliderect(starship.hitbox):
#             self.apply_effect(starship)
#             self.is_active = False
#
#             if self in state.enemy_drops:
#                 state.enemy_drops.remove(self)
#
#             return True
#
#         return False
#
#     def update(self, state) -> None:
#         if not self.is_active:
#             return
#         self.update_rect()
#         self.handle_pickup(state)
#
#     def draw(self, surface: pygame.Surface, camera=None) -> None:
#         if not self.is_active:
#             return
#
#         if camera is None:
#             pygame.draw.rect(surface, self.color, self.rect)
#             return
#
#         screen_x = camera.world_to_screen_x(self.rect.x)
#         screen_y = camera.world_to_screen_y(self.rect.y)
#         size = int(self.SIZE * camera.zoom)
#
#         pygame.draw.rect(surface, self.color, pygame.Rect(screen_x, screen_y, size, size))
