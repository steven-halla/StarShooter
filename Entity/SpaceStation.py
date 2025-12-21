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
        # -------------------------
        # POSITION / SIZE (WORLD SPACE)
        # -------------------------
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

        # -------------------------
        # HP
        # -------------------------
        self.max_hp = max_hp
        self.hp = max_hp

        # -------------------------
        # VISUALS
        # -------------------------
        self.color = GlobalConstants.SKYBLUE
        self.border_color = GlobalConstants.WHITE

    # =========================
    # DAMAGE
    # =========================
    def take_damage(self, damage: int) -> None:
        if self.hp <= 0:
            return

        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def is_destroyed(self) -> bool:
        return self.hp <= 0

    # =========================
    # UPDATE HITBOX (IF NEEDED)
    # =========================
    def update_hitbox(self) -> None:
        self.hitbox.update(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height)
        )

    # =========================
    # DRAW
    # =========================
    def draw(self, surface: pygame.Surface, camera) -> None:
        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        scale = camera.zoom
        w = int(self.width * scale)
        h = int(self.height * scale)

        # Body
        pygame.draw.rect(
            surface,
            self.color,
            (screen_x, screen_y, w, h)
        )

        # Border
        pygame.draw.rect(
            surface,
            self.border_color,
            (screen_x, screen_y, w, h),
            2
        )

        # -------------------------
        # HP BAR (OPTIONAL BUT USEFUL)
        # -------------------------
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
