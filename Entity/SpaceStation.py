import pygame
from Constants.GlobalConstants import GlobalConstants


class SpaceStation:
    def __init__(
        self,
        x: float,
        y: float,
        width: int,
        height: int,
        max_hp: int = 200
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.hitbox = pygame.Rect(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height)
        )

        self.max_hp = max_hp
        self.hp = max_hp

        self.color = GlobalConstants.SKYBLUE
        self.border_color = GlobalConstants.WHITE

    # =========================
    # DAMAGE
    # =========================
    def take_damage(self, damage: int) -> None:
        if self.hp <= 0:
            return
        self.hp = max(0, self.hp - damage)

    def is_destroyed(self) -> bool:
        return self.hp <= 0

    # =========================
    # UPDATE HITBOX
    # ==========================
    def update_hitbox(self, state) -> None:
        # update station hitbox first
        self.hitbox.update(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height)
        )

        # ONLY block player if rects overlap
        ship_rect = state.starship.hitbox
        if self.hitbox.colliderect(ship_rect):
            print(f"Space Station hitbox: {self.hitbox}, Starship hitbox: {ship_rect}")
            print("Collision detected in update_hitbox")
            self.block_player(state)

    # =========================
    # PLAYER COLLISION + BLOCK
    # =========================
    def block_player(self, state) -> None:
        ship = state.starship

        ship_rect = ship.hitbox
        station_rect = self.hitbox

        if not ship_rect.colliderect(station_rect):
            return

        print("!!!!! STARSHIP COLLIDED WITH SPACE STATION !!!!!")

        overlap_left = ship_rect.right - station_rect.left
        overlap_right = station_rect.right - ship_rect.left
        overlap_top = ship_rect.bottom - station_rect.top
        overlap_bottom = station_rect.bottom - ship_rect.top

        min_overlap = min(
            overlap_left,
            overlap_right,
            overlap_top,
            overlap_bottom
        )

        if min_overlap == overlap_left:
            ship_rect.right = station_rect.left
        elif min_overlap == overlap_right:
            ship_rect.left = station_rect.right
        elif min_overlap == overlap_top:
            ship_rect.bottom = station_rect.top
        else:
            ship_rect.top = station_rect.bottom

        ship.x = ship_rect.x
        ship.y = ship_rect.y
        ship.update_hitbox()
    # =========================
    # DRAW
    # =========================
    def draw(self, surface: pygame.Surface, camera) -> None:
        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        scale = camera.zoom
        w = int(self.width * scale)
        h = int(self.height * scale)

        pygame.draw.rect(
            surface,
            self.color,
            (screen_x, screen_y, w, h)
        )

        pygame.draw.rect(
            surface,
            self.border_color,
            (screen_x, screen_y, w, h),
            2
        )

        hp_ratio = self.hp / self.max_hp
        hp_bar_width = int(w * hp_ratio)
        hp_bar_height = 6

        pygame.draw.rect(
            surface,
            (60, 60, 60),
            (screen_x, screen_y - 10, w, hp_bar_height)
        )

        pygame.draw.rect(
            surface,
            (0, 255, 0),
            (screen_x, screen_y - 10, hp_bar_width, hp_bar_height)
        )
