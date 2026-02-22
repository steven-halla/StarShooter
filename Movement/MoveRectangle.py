import pygame
import math
from Constants.GlobalConstants import GlobalConstants


class MoveRectangle:
    def __init__(self):
        pass

    # =====================================================
    # NEW: GENERIC NORMALIZED MOVEMENT
    # =====================================================
    def move_normalized(self, obj, dx: float, dy: float, speed_attr: str = "speed") -> None:
        """
        Move any object using a normalized direction vector.

        dx, dy: direction intent (-1, 0, 1)
        speed_attr: 'speed' (player) or 'moveSpeed' (enemy)
        """

        speed = getattr(obj, speed_attr, 0.0)
        if not isinstance(speed, (float, int)):
            raise TypeError(f"{speed_attr} must be a float or int")
        
        speed = float(speed)

        # No movement
        if dx == 0 and dy == 0:
            return

        # Normalize the vector if its length is greater than 1
        # This prevents diagonal speed increase while allowing 
        # small movements (if dx/dy are less than 1)
        length = math.hypot(dx, dy)
        if length > 1.0:
            dx /= length
            dy /= length

        obj.x += dx * speed
        obj.y += dy * speed

    # =====================================================
    # PLAYER INPUT → NORMALIZED VECTOR
    # =====================================================
    def player_move(self, player) -> None:
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1

        self.move_normalized(player, dx, dy, "speed")

    # =====================================================
    # ENEMY MOVEMENT → NORMALIZED VECTOR
    # =====================================================
    def enemy_move(self, enemy, dx: float, dy: float) -> None:
        """
        Enemy AI supplies dx, dy intent.
        Example: dx=1, dy=0 → move right
        """
        self.move_normalized(enemy, dx, dy, "moveSpeed")

    # =====================================================
    # LEGACY FUNCTIONS (OPTIONAL – SAFE TO KEEP)
    # =====================================================
    def player_move_left(self, obj) -> None:
        self.move_normalized(obj, -1, 0, "speed")

    def player_move_right(self, obj) -> None:
        self.move_normalized(obj, 1, 0, "speed")

    def player_move_up(self, obj) -> None:
        self.move_normalized(obj, 0, -1, "speed")

    def player_move_down(self, obj) -> None:
        self.move_normalized(obj, 0, 1, "speed")

    def enemy_move_left(self, enemy) -> None:
        self.move_normalized(enemy, -1, 0, "moveSpeed")

    def enemy_move_right(self, enemy) -> None:
        self.move_normalized(enemy, 1, 0, "moveSpeed")

    def enemy_move_up(self, enemy) -> None:
        self.move_normalized(enemy, 0, -1, "moveSpeed")

    def enemy_move_down(self, enemy) -> None:
        self.move_normalized(enemy, 0, 1, "moveSpeed")

    # =====================================================
    # VISIBILITY CHECK (UNCHANGED)
    # =====================================================
    def enemy_on_screen(self, enemy, camera):
        if camera is None:
            return False

        screen_y = camera.world_to_screen_y(enemy.y)
        return 0 <= screen_y <= GlobalConstants.GAMEPLAY_HEIGHT
