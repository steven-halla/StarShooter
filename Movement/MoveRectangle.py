import pygame
import math

class MoveRectangle:
    def __init__(self):
        pass

    def _check_multi_input(self) -> float:
        keys = pygame.key.get_pressed()
        directions = [
            keys[pygame.K_LEFT],
            keys[pygame.K_RIGHT],
            keys[pygame.K_UP],
            keys[pygame.K_DOWN],
        ]
        active = sum(directions)
        if active > 1:
            return 1 / math.sqrt(2)
        return 1.0

    def player_move_left(self, obj) -> None:
        if not isinstance(obj.speed, float):
            raise TypeError("speed must be a float")
        modifier = self._check_multi_input()
        obj.x -= obj.speed * modifier
        print(f"x={obj.x}, y={obj.y}, modifier={modifier}")

    def player_move_right(self, obj) -> None:
        if not isinstance(obj.speed, float):
            raise TypeError("speed must be a float")
        modifier = self._check_multi_input()
        obj.x += obj.speed * modifier
        print(f"x={obj.x}, y={obj.y}, modifier={modifier}")

    def player_move_up(self, obj) -> None:
        if not isinstance(obj.speed, float):
            raise TypeError("speed must be a float")
        modifier = self._check_multi_input()
        obj.y -= obj.speed * modifier
        print(f"x={obj.x}, y={obj.y}, modifier={modifier}")

    def player_move_down(self, obj) -> None:
        if not isinstance(obj.speed, float):
            raise TypeError("speed must be a float")
        modifier = self._check_multi_input()
        obj.y += obj.speed * modifier
        print(f"x={obj.x}, y={obj.y}, modifier={modifier}")

    def enemy_move_right(self, enemy) -> None:
        if not isinstance(enemy.moveSpeed, float):
            raise TypeError("moveSpeed must be a float")
        enemy.x += enemy.moveSpeed
