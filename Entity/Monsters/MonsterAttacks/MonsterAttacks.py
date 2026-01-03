# =====================================================
# BARRAGE SPAWN (UNCHANGED GRID)
# =====================================================
import pygame

#----#BARRAGE=====----------------------------------------
def call_barrage(self) -> None:
    self.barrage_rects.clear()
    SIZE = self.BARRAGE_SIZE

    BASE_COORDS = [
        (30, 60), (56, 60), (82, 60), (108, 60),
        (134, 60), (160, 60), (186, 60), (212, 60),
        (238, 60), (264, 60),

        (30, 86), (56, 86), (82, 86), (108, 86),
        (134, 86), (160, 86), (186, 86), (212, 86),
        (238, 86), (264, 86),

        (30, 112), (56, 112), (82, 112), (108, 112),
        (134, 112), (160, 112), (186, 112), (212, 112),
        (238, 112), (264, 112),

        (30, 138), (56, 138), (82, 138), (108, 138),
        (134, 138), (160, 138), (186, 138), (212, 138),
        (238, 138), (264, 138),

        (30, 164), (56, 164), (82, 164), (108, 164),
        (134, 164), (160, 164), (186, 164), (212, 164),
        (238, 164), (264, 164),

        (30, 190), (56, 190), (82, 190), (108, 190),
        (134, 190), (160, 190), (186, 190), (212, 190),
        (238, 190), (264, 190),
    ]

    cam_x = int(self.camera.x)
    cam_y = int(self.camera.y)

    for sx, sy in BASE_COORDS:
        self.barrage_rects.append(
            pygame.Rect(cam_x + sx, cam_y + sy, SIZE, SIZE)
        )

    # =====================================================
    # BARRAGE PHASE CONTROLLER
    # =====================================================
    def update_barrage(self) -> None:
        now = pygame.time.get_ticks()
        elapsed = now - self.barrage_timer

        # 🔴 RED
        if self.barrage_phase == self.PHASE_RED:
            if elapsed >= self.RED_MS:
                self.barrage_phase = self.PHASE_ORANGE
                self.barrage_timer = now

        # 🟧 ORANGE FLASH
        elif self.barrage_phase == self.PHASE_ORANGE:
            if elapsed >= self.ORANGE_MS:
                self.barrage_phase = self.PHASE_OFF
                self.barrage_rects.clear()
                self.barrage_timer = now

        # ❌ OFF
        elif self.barrage_phase == self.PHASE_OFF:
            if elapsed >= self.OFF_MS:
                self.barrage_phase = self.PHASE_RED
                self.call_barrage()
                self.barrage_timer = now


def draw_barrage(self, surface, camera) -> None:
    if self.barrage_phase == self.PHASE_OFF:
        return

    color = (255, 0, 0) if self.barrage_phase == self.PHASE_RED else (255, 165, 0)

    for rect in self.barrage_rects:
        pygame.draw.rect(
            surface,
            color,
            (
                camera.world_to_screen_x(rect.x),
                camera.world_to_screen_y(rect.y),
                rect.width,
                rect.height,
            ),
        )

def apply_barrage_damage(self, player) -> None:
    # Only damage during ORANGE phase
    if self.barrage_phase != self.PHASE_ORANGE:
        return

    if player.invincible:
        return

    player_rect = player.hitbox

    for rect in self.barrage_rects:
        if player_rect.colliderect(rect):
            player.shipHealth -= 30
            player.on_hit()
            return  # only hit once per frame
#----#BARRAGE=====----------------------------------------
