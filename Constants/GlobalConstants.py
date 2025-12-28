import os


class GlobalConstants():
    def __init__(self):
        self.name: str = ""
    #
    # BASE_WINDOW_WIDTH: int = 640
    # BASE_WINDOW_HEIGHT: int = 480

    BASE_WINDOW_WIDTH: int = 800
    BASE_WINDOW_HEIGHT: int = 600
    WINDOWS_SIZE: tuple[int, int] = (BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT)

    UI_PANEL_HEIGHT = 100
    GAMEPLAY_HEIGHT = BASE_WINDOW_HEIGHT - UI_PANEL_HEIGHT

    #colors
    BLACK: tuple[int, int, int] = (0, 0, 0)
    BLUE: tuple[int, int, int] = (0, 0, 255)
    RED: tuple[int, int, int] = (255, 0, 0)
    PURPLE: tuple[int, int, int] = (128, 0, 128)
    YELLOW: tuple[int, int, int] = (255, 255, 0)
    GREY: tuple[int, int, int] = (128, 128, 128)
    PINK: tuple[int, int, int] = (255, 105, 180)
    SKYBLUE = (135, 206, 235)
    WHITE: tuple[int, int, int] = (255, 255, 255)

    FPS: int = 60
    LOWEXP: int = 10
    MEDIUMEXP: int = 20
    HIGHEXP: int = 30
    BOSSEXP: int = 500




