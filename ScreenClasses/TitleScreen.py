# TitleScreen.py
import pygame
from Constants.GlobalConstants import GlobalConstants
from Controller.KeyBoardControls import KeyBoardControls
from Levels import levelThree
from Levels.levelThree import LevelThree


class TitleScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # use SAME controller pattern as rest of game
        self.controls = KeyBoardControls()

        self.font_title = pygame.font.SysFont("arial", 72, bold=True)
        self.font_menu = pygame.font.SysFont("arial", 32)

        # levels 1–10, 12 = SHOP, 11 = LOAD
        self.levels = list(range(1, 11)) + [12, 11]
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

        # UP = previous option
        if self.controls.down_button and not self._up_lock:
            self.selected_index = (self.selected_index - 1) % len(self.levels)
            self._up_lock = True
        elif not self.controls.down_button:
            self._up_lock = False

        # DOWN = next option
        if self.controls.up_button and not self._down_lock:
            self.selected_index = (self.selected_index + 1) % len(self.levels)
            self._down_lock = True
        elif not self.controls.up_button:
            self._down_lock = False

        # FIRE (F)
        if self.controls.main_weapon_button:
            selected_level = self.levels[self.selected_index]

            # -------------------------
            # SHOP KEEPER (LEVEL 12)
            # -------------------------
            if selected_level == 12:
                from ScreenClasses.ShopKeeper import ShopKeeper
                state.currentScreen = ShopKeeper(state.textbox)
                state.currentScreen.start(state)
                return

            # -------------------------
            # LOAD GAME (LEVEL 11)
            # -------------------------
            if selected_level == 11:
                if state.save_state.load_from_file("player_save.json"):
                    # 1) Restore data into the starship object
                    state.save_state.restore_player(state.starship)

                    # 2) Determine which level to load based on the restored current_level
                    from Levels.LevelOne import LevelOne
                    from Levels.LevelTwo import LevelTwo
                    from Levels.levelThree import LevelThree
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

                    # Default to LevelOne if current_level is invalid
                    level_num = state.starship.current_level
                    level_class = LEVEL_MAP.get(level_num, LevelOne)

                    state.currentScreen = level_class(state.textbox)
                    state.currentScreen.start(state)
                return

            # -------------------------
            # NORMAL LEVEL LOAD
            # -------------------------
            from Levels.LevelOne import LevelOne
            from Levels.LevelTwo import LevelTwo
            from Levels.levelThree import LevelThree
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

        # MENU POSITION
        cx = w // 2
        cy = int(h * 0.70)

        up_arrow = self.font_menu.render("▲", True, self.text_color)
        self.screen.blit(up_arrow, up_arrow.get_rect(center=(cx, cy - 50)))

        current = self.levels[self.selected_index]
        if current == 11:
            label = "LOAD GAME"
        elif current == 12:
            label = "SHOP KEEPER"
        else:
            label = f"LEVEL {current}"
        level_surf = self.font_menu.render(label, True, self.highlight_color)
        self.screen.blit(level_surf, level_surf.get_rect(center=(cx, cy)))

        down_arrow = self.font_menu.render("▼", True, self.text_color)
        self.screen.blit(down_arrow, down_arrow.get_rect(center=(cx, cy + 50)))

        pygame.display.flip()
