import pygame

from Constants.GlobalConstants import GlobalConstants
from Movement.MoveRectangle import MoveRectangle


class Enemy:
    def __init__(self):
        self.height: int = 0
        self.width: int = 0
        self.mover: MoveRectangle = MoveRectangle()

        self.color: tuple = GlobalConstants.RED
        self.x: float = 0
        self.y: float = 0

        self.moveSpeed: float = 0.0
        self.enemyHealth: int = 0
        self.enemyBullets: list = []
        self.exp: int = 0
        self.credits: int = 0

        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.camera = None

        # 🔑 IMPORTANT FLAGS
        self.is_on_screen: bool = False
        self.has_entered_screen: bool = False  # ← THIS fixes the swarm

    def update(self):
        self.update_hitbox()

        if self.camera is None:
            return

        # Detect first legitimate entry
        self.is_on_screen = self.mover.enemy_on_screen(self, self.camera)

        if self.is_on_screen:
            self.has_entered_screen = True

        # 🚫 Do NOT clamp until enemy has naturally entered view
        if self.has_entered_screen:
            self._clamp_to_camera()

    def _clamp_to_camera(self) -> None:
        # Horizontal bounds (world space)
        max_x = (self.camera.window_width / self.camera.zoom) - self.width
        if self.x < 0:
            self.x = 0
        elif self.x > max_x:
            self.x = max_x

        # Vertical bounds (world space)
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

    def update_hitbox(self) -> None:
        self.hitbox.update(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height),
        )

    def on_hit(self):
        self.color = (255, 255, 0)
