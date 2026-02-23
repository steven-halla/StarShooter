import pygame
from ScreenClasses.Screen import Screen
from Constants.GlobalConstants import GlobalConstants
from Controller.KeyBoardControls import KeyBoardControls


class HomeBase(Screen):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox
        self._welcome_shown: bool = False

        # background image (top portion)
        self.hangerbay_image = pygame.image.load("Assets/Images/hangerbay.png").convert()

        # RIGHT SIDE RECT
        display_w, display_h = pygame.display.get_surface().get_size()
        self.right_panel_rect = pygame.Rect(
            display_w - 175,
            (display_h - 500) // 2,
            150,
            325
        )

        # menu text
        self.menu_font = pygame.font.SysFont("arial", 20)
        self.menu_items: list[str] = ["W. Shop", "D. Shop", "N. Mission"]
        self.weapon_shop_descriptions: dict[str, str] = {
            "m. gun damage booster": "Machine Gun Damage Booster\nIncreases your machine gun damage.",
            "missile speed booster": "Missile Speed Booster\nIncreases your missile speed.",
            "Metal Shield": "Metal Shield\nUse Ki to create a metal shield that rotates around the ship that damages enemies/bullets on contact.",
        }
        self.defense_shop_descriptions: dict[str, str] = {
            "Armor Plating": "adds +50 HP to hull.",
            "Shield Generator": "Provides + 25 shields",
            "Ki Efficiency chip": "Adds +25 KI to user.",
        }
        self.menu_padding_x: int = 45
        self.menu_padding_y: int = 16
        self.menu_line_gap: int = 14

        # arrow / selection
        self.menu_index: int = 0
        self.arrow_text: str = "->"
        self.arrow_gap: int = 10
        self.upper_padding: int = 12

        # input locks
        self._up_lock: bool = False
        self._down_lock: bool = False
        self._f_lock: bool = False

        # weapon shop popup state
        self.weapon_shop_open: bool = False
        self.weapon_shop_index: int = 0
        self.weapon_shop_items: list[str] = [
            "m. gun damage booster",
            "missile speed booster",
            "Metal Shield"
        ]

        # defense shop popup state
        self.defense_shop_open: bool = False
        self.defense_shop_index: int = 0
        self.defense_shop_items: list[str] = [
            "Armor Plating",
            "Shield Generator",
            "Ki Efficiency chip"
        ]

        # shop rects (400x400 centered)
        self.weapon_shop_rect = pygame.Rect(0, 0, 450, 400)
        self.defense_shop_rect = pygame.Rect(0, 0, 450, 400)
        self.shop_border_thickness: int = 4

        self.last_weapon_shop_index: int = -1
        self.last_defense_shop_index: int = -1


    def start(self, state) -> None:
        super().start(state)

        if not self._welcome_shown:
            self.textbox.show("Welcome to your home base")
            self._welcome_shown = True

        # ensure shop rects are centered once we have a display
        w, h = state.DISPLAY.get_size()
        self.weapon_shop_rect.center = (w // 2 - 50, h // 2 - 80)
        self.defense_shop_rect.center = (w // 2 - 50, h // 2 - 80)

    def update(self, state):
        super().update(state)

        if not hasattr(self, "controls"):
            self.controls = KeyBoardControls()

        self.controls.update()

        # ADVANCE TEXTBOX (Q)
        if self.controls.q_just_pressed_button:
            self.textbox.advance()

        # MENU NAV (disabled while popup open)
        if not self.weapon_shop_open and not self.defense_shop_open:
            if self.controls.up_button and not self.up_lock:
                self.menu_index -= 1
                if self.menu_index < 0:
                    self.menu_index = 0
                self.up_lock = True
            elif not self.controls.up_button:
                self.up_lock = False

            if self.controls.down_button and not self.down_lock:
                self.menu_index += 1
                if self.menu_index > len(self.menu_items) - 1:
                    self.menu_index = len(self.menu_items) - 1
                self.down_lock = True
            elif not self.controls.down_button:
                self.down_lock = False
        elif self.weapon_shop_open:
            # Weapon Shop navigation
            if self.controls.up_button and not self.up_lock:
                self.weapon_shop_index -= 1
                if self.weapon_shop_index < 0:
                    self.weapon_shop_index = 0
                self.up_lock = True
            elif not self.controls.up_button:
                self.up_lock = False

            if self.controls.down_button and not self.down_lock:
                self.weapon_shop_index += 1
                if self.weapon_shop_index > len(self.weapon_shop_items) - 1:
                    self.weapon_shop_index = len(self.weapon_shop_items) - 1
                self.down_lock = True
            elif not self.controls.down_button:
                self.down_lock = False

            # SHOW DESCRIPTION IN TEXTBOX WHEN SELECTION CHANGES
            if self.weapon_shop_index != self.last_weapon_shop_index:
                item = self.weapon_shop_items[self.weapon_shop_index]
                self.textbox.show(self.weapon_shop_descriptions.get(item, item))
                self.last_weapon_shop_index = self.weapon_shop_index
        elif self.defense_shop_open:
            # Defense Shop navigation
            if self.controls.up_button and not self.up_lock:
                self.defense_shop_index -= 1
                if self.defense_shop_index < 0:
                    self.defense_shop_index = 0
                self.up_lock = True
            elif not self.controls.up_button:
                self.up_lock = False

            if self.controls.down_button and not self.down_lock:
                self.defense_shop_index += 1
                if self.defense_shop_index > len(self.defense_shop_items) - 1:
                    self.defense_shop_index = len(self.defense_shop_items) - 1
                self.down_lock = True
            elif not self.controls.down_button:
                self.down_lock = False

            # SHOW DESCRIPTION IN TEXTBOX WHEN SELECTION CHANGES
            if self.defense_shop_index != self.last_defense_shop_index:
                item = self.defense_shop_items[self.defense_shop_index]
                self.textbox.show(self.defense_shop_descriptions.get(item, item))
                self.last_defense_shop_index = self.defense_shop_index

        # OPEN SHOPS (Primary fire key = F)
        if not self.weapon_shop_open and not self.defense_shop_open:
            if self.controls.main_weapon_button and not self.f_lock:
                if self.menu_index == 0:
                    self.weapon_shop_open = True
                    self.last_weapon_shop_index = -1  # force first description show
                elif self.menu_index == 1:
                    self.defense_shop_open = True
                    self.last_defense_shop_index = -1  # force first description show
                self.f_lock = True
            elif not self.controls.main_weapon_button:
                self.f_lock = False
        elif self.weapon_shop_open:
            # PURCHASE LOGIC (Primary fire key = F) while shop is open
            if self.controls.main_weapon_button and not self.f_lock:
                item = self.weapon_shop_items[self.weapon_shop_index]
                if item == "Metal Shield":
                    price = 500
                    if state.starship.money >= price:
                        if "Metal Shield" not in state.starship.magic_inventory:
                            state.starship.money -= price
                            state.starship.magic_inventory.append("Metal Shield")
                            self.textbox.show(f"Purchased Metal Shield for {price}!")
                        else:
                            self.textbox.show("You already have Metal Shield.")
                    else:
                        self.textbox.show(f"Not enough money for Metal Shield (Need {price}).")
                self.f_lock = True
            elif not self.controls.main_weapon_button:
                self.f_lock = False
        elif self.defense_shop_open:
            # PURCHASE LOGIC (Primary fire key = F) while shop is open
            if self.controls.main_weapon_button and not self.f_lock:
                item = self.defense_shop_items[self.defense_shop_index]
                # Placeholder logic for defense shop items
                self.textbox.show(f"Selected {item} for purchase (Not yet implemented).")
                self.f_lock = True
            elif not self.controls.main_weapon_button:
                self.f_lock = False

        # CLOSE SHOPS (Magic 1 key = D) keep same behavior using release flag
        if self.weapon_shop_open and self.controls.magic_1_released:
            self.weapon_shop_open = False
            self.last_weapon_shop_index = -1
        if self.defense_shop_open and self.controls.magic_1_released:
            self.defense_shop_open = False
            self.last_defense_shop_index = -1
    def draw_upper_home_base_screen(self, state) -> None:
        text_box_rect = self.textbox.rect

        top_area = pygame.Rect(
            0,
            0,
            state.DISPLAY.get_width(),
            max(0, text_box_rect.top - self.upper_padding),
        )

        if top_area.height <= 0:
            return

        img_w, img_h = self.hangerbay_image.get_size()
        scale = min(top_area.width / img_w, top_area.height / img_h)

        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        scaled = pygame.transform.scale(self.hangerbay_image, (new_w, new_h))

        x = top_area.x + (top_area.width - new_w) // 2 - 100
        y = top_area.y + (top_area.height - new_h) // 2

        state.DISPLAY.blit(scaled, (x, y))

    def weapon_shop_rectangle(self, state) -> None:
        if not self.weapon_shop_open:
            return

        # black background fill inside the popup
        pygame.draw.rect(state.DISPLAY, (0, 0, 0), self.weapon_shop_rect)

        # thick white border
        pygame.draw.rect(
            state.DISPLAY,
            (255, 255, 255),
            self.weapon_shop_rect,
            self.shop_border_thickness,
        )

        # items
        x = self.weapon_shop_rect.x + 50
        y = self.weapon_shop_rect.y + 18

        title_font = pygame.font.SysFont("arial", 24)
        item_font = pygame.font.SysFont("arial", 20)

        title_surf = title_font.render("Weapon Shop", True, (255, 255, 255))
        state.DISPLAY.blit(title_surf, (x , y))
        y += title_surf.get_height() + 20

        arrow_surf = self.menu_font.render(self.arrow_text, True, (255, 255, 255))
        arrow_x = x - arrow_surf.get_width() - self.arrow_gap

        for i, item in enumerate(self.weapon_shop_items):
            if i == self.weapon_shop_index:
                state.DISPLAY.blit(arrow_surf, (arrow_x, y))

            surf = item_font.render(item, True, (255, 255, 255))
            state.DISPLAY.blit(surf, (x, y))
            y += surf.get_height() + 14

    def defense_shop_rectangle(self, state) -> None:
        if not self.defense_shop_open:
            return

        # black background fill inside the popup
        pygame.draw.rect(state.DISPLAY, (0, 0, 0), self.defense_shop_rect)

        # thick white border
        pygame.draw.rect(
            state.DISPLAY,
            (255, 255, 255),
            self.defense_shop_rect,
            self.shop_border_thickness,
        )

        # items
        x = self.defense_shop_rect.x + 50
        y = self.defense_shop_rect.y + 18

        title_font = pygame.font.SysFont("arial", 24)
        item_font = pygame.font.SysFont("arial", 20)

        title_surf = title_font.render("Defense Shop", True, (255, 255, 255))
        state.DISPLAY.blit(title_surf, (x, y))
        y += title_surf.get_height() + 20

        arrow_surf = self.menu_font.render(self.arrow_text, True, (255, 255, 255))
        arrow_x = x - arrow_surf.get_width() - self.arrow_gap

        for i, item in enumerate(self.defense_shop_items):
            if i == self.defense_shop_index:
                state.DISPLAY.blit(arrow_surf, (arrow_x, y))

            surf = item_font.render(item, True, (255, 255, 255))
            state.DISPLAY.blit(surf, (x, y))
            y += surf.get_height() + 14
    def draw(self, state):
        state.DISPLAY.fill(GlobalConstants.BLACK)

        self.draw_upper_home_base_screen(state)

        # box
        pygame.draw.rect(state.DISPLAY, (255, 255, 255), self.right_panel_rect, 4)

        # text inside box + arrow
        base_x = self.right_panel_rect.x + self.menu_padding_x
        y = self.right_panel_rect.y + self.menu_padding_y

        arrow_surf = self.menu_font.render(self.arrow_text, True, (255, 255, 255))
        arrow_x = base_x - arrow_surf.get_width() - self.arrow_gap

        for i, item in enumerate(self.menu_items):
            if i == self.menu_index and not self.weapon_shop_open and not self.defense_shop_open:
                state.DISPLAY.blit(arrow_surf, (arrow_x, y))

            surf = self.menu_font.render(item, True, (255, 255, 255))
            state.DISPLAY.blit(surf, (base_x, y))
            y += surf.get_height() + self.menu_line_gap

        # popups (overlaps image)
        self.weapon_shop_rectangle(state)
        self.defense_shop_rectangle(state)

        self.textbox.draw(state.DISPLAY)

        pygame.display.flip()
