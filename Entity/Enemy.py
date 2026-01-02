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
        self.last_enemy_health: int = self.enemyHealth

        self.enemyBullets: list = []
        self.exp: int = 0
        self.credits: int = 0

        # rendering / damage flash
        self.is_flashing: bool = False
        self.flash_start_time: int = 0
        self.flash_duration_ms: int = 120
        self.flash_interval_ms: int = 30

        # references (set by level)
        self.camera = None
        self.target_player = None

        # collision
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

        # state flags
        self.is_on_screen: bool = False
        self.has_entered_screen: bool = False
        self.is_active: bool = False
        self.enemy_list: list[Enemy] = []

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update(self):
        self.update_hitbox()

        if self.camera is None:
            self.is_active = False
            return

        self._clamp_horizontal()
        self.is_on_screen = self.mover.enemy_on_screen(self, self.camera)

        if self.is_on_screen and self.player_in_vicinity():
            self.is_active = True
            self.has_entered_screen = True
            self._clamp_vertical()
        else:
            self.is_active = False

        # 🔑 DAMAGE DETECTION (THIS IS THE KEY)
        if self.enemyHealth < self.last_enemy_health:
            self.is_flashing = True
            self.flash_start_time = pygame.time.get_ticks()

        self.last_enemy_health = self.enemyHealth

        # 🔑 FLASH TIMER
        if self.is_flashing:
            if pygame.time.get_ticks() - self.flash_start_time >= self.flash_duration_ms:
                self.is_flashing = False
    # --------------------------------------------------
    # DAMAGE
    # --------------------------------------------------
    def take_damage(self, amount: int) -> None:
        self.enemyHealth -= amount
        self.is_flashing = True
        self.flash_start_time = pygame.time.get_ticks()

    # --------------------------------------------------
    # DRAW DAMAGE FLASH (CALLED AFTER CHILD DRAW)
    # --------------------------------------------------
    def draw(self, surface: pygame.Surface, camera) -> None:
        # Don't draw if not active (e.g., removed due to collision with UI panel)
        if not self.is_active:
            return

        if not self.is_flashing:
            return

        elapsed = pygame.time.get_ticks() - self.flash_start_time
        if elapsed >= self.flash_duration_ms:
            self.is_flashing = False
            return

        # blink timing
        if (elapsed // self.flash_interval_ms) % 2 != 0:
            return

        x = camera.world_to_screen_x(self.hitbox.x)
        y = camera.world_to_screen_y(self.hitbox.y)
        w = int(self.hitbox.width * camera.zoom)
        h = int(self.hitbox.height * camera.zoom)

        flash = pygame.Surface((w, h), pygame.SRCALPHA)
        flash.fill((*GlobalConstants.RED, 160))
        surface.blit(flash, (x, y))

    # --------------------------------------------------
    # CLAMPING
    # --------------------------------------------------
    def _clamp_horizontal(self) -> None:
        max_x = (self.camera.window_width / self.camera.zoom) - self.width
        self.x = max(0, min(self.x, max_x))

    def _clamp_vertical(self) -> None:
        cam_top = self.camera.y
        cam_bottom = (
            self.camera.y
            + (self.camera.window_height / self.camera.zoom)
            - self.height
        )
        self.y = max(cam_top, min(self.y, cam_bottom))

    # --------------------------------------------------
    # PROXIMITY
    # --------------------------------------------------
    def player_in_vicinity(self) -> bool:
        if self.camera is None or self.target_player is None:
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

    def draw_damage_flash(self, surface: pygame.Surface, camera) -> None:
        # Don't draw if not active (e.g., removed due to collision with UI panel)
        if not self.is_active:
            return

        if not self.is_flashing:
            return

        elapsed = pygame.time.get_ticks() - self.flash_start_time
        if elapsed >= self.flash_duration_ms:
            self.is_flashing = False
            return

        if (elapsed // self.flash_interval_ms) % 2 != 0:
            return

        x = camera.world_to_screen_x(self.hitbox.x)
        y = camera.world_to_screen_y(self.hitbox.y)
        w = int(self.hitbox.width * camera.zoom)
        h = int(self.hitbox.height * camera.zoom)

        flash = pygame.Surface((w, h), pygame.SRCALPHA)
        flash.fill((*GlobalConstants.RED, 160))
        surface.blit(flash, (x, y))
