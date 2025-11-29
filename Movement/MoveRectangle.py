
class MoveRectangle:
    def __init__(self):
        pass

    def move_left(self, obj) -> None:
        if not isinstance(obj.speed, float):
            raise TypeError("speed must be a float")
        obj.x -= obj.speed

    def move_right(self, obj) -> None:
        if not isinstance(obj.speed, float):
            raise TypeError("speed must be a float")
        obj.x += obj.speed

    def move_up(self, obj) -> None:
        if not isinstance(obj.speed, float):
            raise TypeError("speed must be a float")
        obj.y -= obj.speed

    def move_down(self, obj) -> None:
        if not isinstance(obj.speed, float):
            raise TypeError("speed must be a float")
        obj.y += obj.speed
