import pygame

from Constants.GlobalConstants import GlobalConstants
from Movement.MoveRectangle import MoveRectangle


class Enemy:
    def __init__(self):
        # size
        self.width: int = 0
        self.height: int = 0

        # position (WORLD space)
        self.x: float = 0
        self.y: float = 0

        # movement
        self.moveSpeed: float = 0.0
        self.mover: MoveRectangle = MoveRectangle()

        # combat / stats
        self.enemyHealth: int = 0
        self.enemyBullets: list = []
        self.exp: int = 0
        self.credits: int = 0

        # rendering
        self.color = GlobalConstants.RED

        # references (set by level)
        self.camera = None
        self.target_player = None

        # collision
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

        # state flags
        self.is_on_screen: bool = False
        self.has_entered_screen: bool = False
        self.is_active: bool = False  # 🔑 THIS IS THE KEY

    # --------------------------------------------------
    # UPDATE (GLOBAL RULES ONLY)
    # --------------------------------------------------
    def update(self):
        self.update_hitbox()
        # print("TARGET:", self.target_player)  # ← TEMP DEBUG

        if self.camera is None:
            self.is_active = False
            return

        # horizontal clamp ALWAYS
        self._clamp_horizontal()

        # visibility
        self.is_on_screen = self.mover.enemy_on_screen(self, self.camera)

        # activation gate
        if self.is_on_screen and self.player_in_vicinity():
            self.is_active = True
            self.has_entered_screen = True
            self._clamp_vertical()
        else:
            self.is_active = False

    # --------------------------------------------------
    # CLAMPING
    # --------------------------------------------------
    def _clamp_horizontal(self) -> None:
        max_x = (self.camera.window_width / self.camera.zoom) - self.width
        if self.x < 0:
            self.x = 0
        elif self.x > max_x:
            self.x = max_x

    def _clamp_vertical(self) -> None:
        cam_top = self.camera.y
        cam_bottom = (
            self.camera.y
            + (self.camera.window_height / self.camera.zoom)
            - self.height
        )

        if self.y < cam_top:
            self.y = cam_top
        elif self.y > cam_bottom:
            self.y = cam_bottom

    # --------------------------------------------------
    # PLAYER PROXIMITY GATE
    # --------------------------------------------------
    def player_in_vicinity(self) -> bool:
        if self.camera is None or self.target_player is None:
            return False

        enemy_screen_y = self.camera.world_to_screen_y(self.y)
        player_screen_y = self.camera.world_to_screen_y(self.target_player.y)

        window_h = self.camera.window_height

        if not (0 <= enemy_screen_y <= window_h):
            return False
        if not (0 <= player_screen_y <= window_h):
            return False

        dx = abs(self.x - self.target_player.x)
        dy = abs(self.y - self.target_player.y)

        return dx <= 400 and dy <= 300

    # --------------------------------------------------
    # HITBOX
    # --------------------------------------------------
    def update_hitbox(self) -> None:
        self.hitbox.update(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height),
        )

    # --------------------------------------------------
    # DAMAGE HOOK
    # --------------------------------------------------
    def on_hit(self):
        self.color = (255, 255, 0)
