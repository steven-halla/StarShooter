# TitleScreen.py
import pygame
from Constants.GlobalConstants import GlobalConstants
from Controller.KeyBoardControls import KeyBoardControls
from Levels.levelThree import LevelThree


class TitleScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # use SAME controller pattern as rest of game
        self.controls = KeyBoardControls()

        self.font_title = pygame.font.SysFont("arial", 72, bold=True)
        self.font_menu = pygame.font.SysFont("arial", 32)

        # levels 1–10
        self.levels = list(range(1, 11))
        self.selected_index = 0

        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.highlight_color = (0, 200, 255)

        # one-tap locks
        self._up_lock = False
        self._down_lock = False

    # REQUIRED BY ENGINE
    def start(self, state) -> None:
        pass

    # REQUIRED BY ENGINE
    def update(self, state) -> None:
        self.controls.update()

        # UP = previous level
        if self.controls.down_button and not self._up_lock:
            self.selected_index = (self.selected_index - 1) % len(self.levels)
            self._up_lock = True
        elif not self.controls.down_button:
            self._up_lock = False

        # DOWN = next level
        if self.controls.up_button and not self._down_lock:
            self.selected_index = (self.selected_index + 1) % len(self.levels)
            self._down_lock = True
        elif not self.controls.up_button:
            self._down_lock = False

        # 🔑 FIRE (F) → SWITCH LEVEL
        if self.controls.main_weapon_button:
            selected_level = self.levels[self.selected_index]

            # LEVEL MAP (LOCAL, NO IMPORT CYCLE)
            from Levels.LevelOne import LevelOne
            from Levels.LevelTwo import LevelTwo
            from Levels.LevelFour import LevelFour
            from Levels.LevelFive import LevelFive
            from Levels.LevelSix import LevelSix
            from Levels.LevelSeven import LevelSeven
            from Levels.LevelEight import LevelEight
            from Levels.LevelNine import LevelNine
            from Levels.LevelTen import LevelTen

            LEVEL_MAP = {
                1: LevelOne,
                2: LevelTwo,
                3: LevelThree,
                4: LevelFour,
                5: LevelFive,
                6: LevelSix,
                7: LevelSeven,
                8: LevelEight,
                9: LevelNine,
                10: LevelTen,
            }

            level_class = LEVEL_MAP[selected_level]
            state.currentScreen = level_class(state.textbox)
            state.currentScreen.start(state)

    # REQUIRED BY ENGINE
    def draw(self, state) -> None:
        self.screen.fill(self.bg_color)
        w, h = self.screen.get_size()

        # TITLE
        title_surf = self.font_title.render("STAR SHOOTER", True, self.text_color)
        self.screen.blit(
            title_surf,
            title_surf.get_rect(center=(w // 2, h // 4))
        )

        # LEVEL SELECT (BOTTOM MIDDLE)
        cx = w // 2
        cy = int(h * 0.70)

        up_arrow = self.font_menu.render("▲", True, self.text_color)
        self.screen.blit(up_arrow, up_arrow.get_rect(center=(cx, cy - 50)))

        level_text = f"LEVEL {self.levels[self.selected_index]}"
        level_surf = self.font_menu.render(level_text, True, self.highlight_color)
        self.screen.blit(level_surf, level_surf.get_rect(center=(cx, cy)))

        down_arrow = self.font_menu.render("▼", True, self.text_color)
        self.screen.blit(down_arrow, down_arrow.get_rect(center=(cx, cy + 50)))

        pygame.display.flip()
