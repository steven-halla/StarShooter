import pygame
from Constants.GlobalConstants import GlobalConstants


class EnemyDrop:
    SIZE: int = 16

    DROP_HEALTH: str = "BLUE"
    DROP_SHIELD: str = "PURPLE"
    DROP_MISSILE: str = "YELLOW"

    def __init__(self, x: float, y: float, drop_type: str):
        self.x: float = float(x)
        self.y: float = float(y)
        self.drop_type: str = drop_type

        if drop_type == self.DROP_HEALTH:
            self.color = GlobalConstants.BLUE
        elif drop_type == self.DROP_SHIELD:
            self.color = GlobalConstants.PURPLE
        elif drop_type == self.DROP_MISSILE:
            self.color = GlobalConstants.YELLOW
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
                    starship.shield_system.current_shield_points + 10,
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

    def handle_pickup(self, state) -> bool:
        if not self.is_active:
            return False

        starship = state.starship
        # Check collision with starship hitbox.
        # Ensure we use world coordinates for the check.
        if self.rect.colliderect(starship.hitbox):
            self.apply_effect(starship)
            self.is_active = False

            if self in state.enemy_drops:
                state.enemy_drops.remove(self)

            return True

        return False

    def update(self, state) -> None:
        if not self.is_active:
            return
        self.update_rect()
        self.handle_pickup(state)

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
