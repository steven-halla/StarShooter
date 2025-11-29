class MoveRectangle:
    def __init__(self):
        pass

    def move_left(self, obj) -> None:
        # FLOAT ONLY for speed
        if not isinstance(obj.speed, float):
            raise TypeError("speed must be a float")


        obj.x -= obj.speed
