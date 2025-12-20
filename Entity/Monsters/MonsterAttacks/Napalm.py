import pygame
import math


class Napalm:
    def __init__(
        self,
        start_x: float,
        start_y: float,
        target_x: float,
        target_y: float,
        travel_distance: float = 100.0,
        travel_speed: float = 4.0,
        aoe_duration_ms: int = 3000,
        width: int = 50,
        height: int = 50,
        damage: int = 5,
    ) -> None:
        # position
        self.x = start_x
        self.y = start_y

        # size
        self.width = width
        self.height = height

        # damage
        self.damage = damage

        # rect (WORLD space)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # direction toward player
        dx = target_x - start_x
        dy = target_y - start_y
        dist = max(1, math.hypot(dx, dy))

        self.dir_x = dx / dist
        self.dir_y = dy / dist

        # travel
        self.travel_speed = travel_speed
        self.travel_distance = travel_distance
        self.distance_traveled = 0.0
        self.is_moving = True

        # timers
        self.spawn_time = pygame.time.get_ticks()
        self.aoe_duration_ms = aoe_duration_ms
        self.stop_time = None
        # state
        self.is_active = True

    # ---------------- UPDATE ----------------
    def update(self) -> None:
        now = pygame.time.get_ticks()

        # MOVE until travel distance reached
        if self.is_moving:
            step_x = self.dir_x * self.travel_speed
            step_y = self.dir_y * self.travel_speed

            self.x += step_x
            self.y += step_y
            self.distance_traveled += math.hypot(step_x, step_y)

            if self.distance_traveled >= self.travel_distance:
                self.is_moving = False
                self.stop_time = now

        # AOE lifetime
        if not self.is_moving and self.stop_time is not None:
            if now - self.stop_time >= self.aoe_duration_ms:
                self.is_active = False

        self.rect.topleft = (self.x, self.y)

    # ---------------- DRAW ----------------
    def draw(self, surface: pygame.Surface, camera) -> None:
        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        draw_rect = pygame.Rect(
            screen_x,
            screen_y,
            int(self.width * camera.zoom),
            int(self.height * camera.zoom),
        )

        pygame.draw.rect(surface, (255, 120, 0), draw_rect)

    # ---------------- COLLISION ----------------
    def hits(self, target_rect: pygame.Rect) -> bool:
        return self.rect.colliderect(target_rect)
