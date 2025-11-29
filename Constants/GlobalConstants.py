

class GlobalConstants():
    def __init__(self):
        self.name: str = ""

    BASE_WINDOW_HEIGHT: int = 800
    BASE_WINDOW_WIDTH: int = 1200
    WINDOWS_SIZE: tuple[int, int] = (BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT)

    BLACK: tuple[int, int, int] = (0, 0, 0)
    BLUE: tuple[int, int, int] = (0, 0, 255)
    RED: tuple[int, int, int] = (255, 0, 0)
    FPS: int = 60

