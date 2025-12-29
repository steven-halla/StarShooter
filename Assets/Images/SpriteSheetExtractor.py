import pygame
from typing import List


import pygame
from typing import List


class SpriteSheetExtractor:
    """
    Utility for extracting sprites from sprite sheets
    using explicit layout methods.
    """

    def __init__(self, image_path: str) -> None:
        # SAME PATTERN YOU ALREADY USE EVERYWHERE ELSE
        # relative to project root / working directory
        self.sheet: pygame.Surface = pygame.image.load(image_path).convert_alpha()

    # -------------------------------------------------
    # HORIZONTAL STRIP (one row)
    # -------------------------------------------------
    def extract_horizontal(
        self,
        sprite_width: int,
        sprite_height: int,
        count: int | None = None
    ) -> List[pygame.Surface]:
        sheet_width = self.sheet.get_width()

        if count is None:
            count = sheet_width // sprite_width

        sprites: List[pygame.Surface] = []

        for i in range(count):
            rect = pygame.Rect(
                i * sprite_width,
                0,
                sprite_width,
                sprite_height
            )
            sprites.append(self.sheet.subsurface(rect))

        return sprites

    # -------------------------------------------------
    # VERTICAL STRIP (one column)
    # -------------------------------------------------
    def extract_vertical(
        self,
        sprite_width: int,
        sprite_height: int,
        count: int | None = None
    ) -> List[pygame.Surface]:
        sheet_height = self.sheet.get_height()

        if count is None:
            count = sheet_height // sprite_height

        sprites: List[pygame.Surface] = []

        for i in range(count):
            rect = pygame.Rect(
                0,
                i * sprite_height,
                sprite_width,
                sprite_height
            )
            sprites.append(self.sheet.subsurface(rect))

        return sprites

    # -------------------------------------------------
    # GRID (rows x columns)
    # -------------------------------------------------
    def extract_grid(
        self,
        sprite_width: int,
        sprite_height: int,
        rows: int,
        columns: int
    ) -> List[pygame.Surface]:
        sprites: List[pygame.Surface] = []

        for row in range(rows):
            for col in range(columns):
                rect = pygame.Rect(
                    col * sprite_width,
                    row * sprite_height,
                    sprite_width,
                    sprite_height
                )
                sprites.append(self.sheet.subsurface(rect))

        return sprites

    # -------------------------------------------------
    # CUSTOM RECTS (manual control)
    # -------------------------------------------------
    def extract_custom(
        self,
        rects: List[pygame.Rect]
    ) -> List[pygame.Surface]:
        sprites: List[pygame.Surface] = []

        for rect in rects:
            sprites.append(self.sheet.subsurface(rect))

        return sprites
