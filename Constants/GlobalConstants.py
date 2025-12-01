import os


class GlobalConstants():
    def __init__(self):
        self.name: str = ""

    BASE_WINDOW_HEIGHT: int = 800
    BASE_WINDOW_WIDTH: int = 900
    WINDOWS_SIZE: tuple[int, int] = (BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT)

    BLACK: tuple[int, int, int] = (0, 0, 0)
    BLUE: tuple[int, int, int] = (0, 0, 255)
    RED: tuple[int, int, int] = (255, 0, 0)
    PURPLE: tuple[int, int, int] = (128, 0, 128)
    YELLOW: tuple[int, int, int] = (255, 255, 0)
    GREY: tuple[int, int, int] = (128, 128, 128)
    PINK: tuple[int, int, int] = (255, 105, 180)
    FPS: int = 60
    LOWEXP: int = 10
    MEDIUMEXP: int = 20
    HIGHEXP: int = 30
    BOSSEXP: int = 500




