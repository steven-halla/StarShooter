import pygame
from SaveStates.SaveState import SaveState
from ScreenClasses.Screen import Screen
from Constants.GlobalConstants import GlobalConstants
from Controller.KeyBoardControls import KeyBoardControls


class HomeBase(Screen):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox
        self._welcome_shown: bool = False
        self.save_state = SaveState()

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
        self.menu_items: list[str] = ["W. Shop", "D. Shop", "N. Mission", "Save", "Load"]
        self.weapon_shop_descriptions: dict[str, str] = {
            "M. gun damage booster": "Flesh Rotter Rounds, does extra damage.",
            "Missile speed booster": "Missile Speed Booster\nIncreases your missile speed.",
            "Metal Shield": "Metal Shield\nUse Ki to create a metal shield that rotates around the ship that damages enemies.",
            "Wind Slicer": "Wind Slicer\n Bullets laced with nerve shredder chemicals.",
            "Missile Count +1": "Increases your max missile count.",
        }
        self.defense_shop_descriptions: dict[str, str] = {
            "Armor Plating": "adds +50 HP to hull.",
            "Shield Generator": "Provides + 25 shields",
            "Ki Efficiency chip": "Adds +25 KI to user.",
            "Shield Charger": "Faster Recharge rate for shields.",
            "Speed up": "Ship moves faster.",
        }
        self.menu_padding_x: int = 45
        self.menu_padding_y: int = 16
        self.menu_line_gap: int = 14

        # arrow / selection
        self.menu_index: int = 0
        self.arrow_text: str = "->"
        self.arrow_gap: int = 10
        self.upper_padding: int = 12

        self.money_font = pygame.font.SysFont("arial", 22, bold=True)

        # shop levels data
        self.weapon_shop_levels = {
            1: ["M. gun damage booster", "Missile speed booster", "Metal Shield"],
            2: ["Wind Slicer", "Missile Count +1"]
        }
        self.defense_shop_levels = {
            1: ["Armor Plating", "Shield Generator", "Ki Efficiency chip"],
            2: ["Shield Charger", "Speed up"]
        }
        self.item_prices = {
            "M. gun damage booster": 5000,
            "Missile speed booster": 5000,
            "Metal Shield": 5000,
            "Wind Slicer": 10000,
            "Missile Count +1": 10000,
            "Armor Plating": 5000,
            "Shield Generator": 5000,
            "Ki Efficiency chip": 5000,
            "Shield Charger": 10000,
            "Speed up": 10000
        }

        # input locks
        self._up_lock: bool = False
        self._down_lock: bool = False
        self._f_lock: bool = False

        # weapon shop popup state
        self.weapon_shop_open: bool = False
        self.weapon_shop_index: int = 0
        self.weapon_shop_items: list[str] = []

        # defense shop popup state
        self.defense_shop_open: bool = False
        self.defense_shop_index: int = 0
        self.defense_shop_items: list[str] = []

        # shop rects (400x400 centered)
        self.weapon_shop_rect = pygame.Rect(0, 0, 450, 400)
        self.defense_shop_rect = pygame.Rect(0, 0, 450, 400)
        self.shop_border_thickness: int = 4

        self.last_weapon_shop_index: int = -1
        self.last_defense_shop_index: int = -1
        self.show_mission_briefing = False



    def start(self, state) -> None:
        super().start(state)
        state.starship.shipHealth = state.starship.shipHealthMax
        state.starship.shield_system.reset()
        state.starship.player_ki = state.starship.player_max_ki
        state.starship.missile.current_missiles = state.starship.missile.max_missiles

        # Save game when arriving at Home Base
        self.save_state.set_location_home_base()
        self.save_state.capture_player(state.starship)
        self.save_state.save_to_file("player_save.json")

        if not self._welcome_shown:
            self.textbox.show("Welcome to your home base")
            self._welcome_shown = True

        # ensure shop rects are centered once we have a display
        w, h = state.DISPLAY.get_size()
        self.weapon_shop_rect.center = (w // 2 - 50, h // 2 - 80)
        self.defense_shop_rect.center = (w // 2 - 50, h // 2 - 80)

    def update(self, state):
        super().update(state)
        # print(state.starship.machine_gun_damage)

        # Update shops based on current level (cumulative)
        self.weapon_shop_items = []
        self.defense_shop_items = []
        for level in range(1, state.starship.current_level + 1):
            if level in self.weapon_shop_levels:
                self.weapon_shop_items.extend(self.weapon_shop_levels[level])
            if level in self.defense_shop_levels:
                self.defense_shop_items.extend(self.defense_shop_levels[level])

        if not hasattr(self, "controls"):
            self.controls = KeyBoardControls()

        self.controls.update()

        # Magic Cycling
        if self.controls.magic_cycle_just_pressed:
            inventory = state.starship.magic_inventory
            if inventory:
                current_magic = state.starship.equipped_magic[0]
                try:
                    current_index = inventory.index(current_magic)
                    next_index = (current_index + 1) % len(inventory)
                except ValueError:
                    next_index = 0
                state.starship.equipped_magic[0] = inventory[next_index]
                print(f"Equipped magic 0: {state.starship.equipped_magic[0]}")

        # ADVANCE TEXTBOX (Q)
        if self.controls.q_just_pressed_button:
            self.textbox.advance()

        # MENU NAV (disabled while popup open)
        if not self.weapon_shop_open and not self.defense_shop_open:
            if self.controls.up_button and not self._up_lock:
                self.menu_index -= 1
                if self.menu_index < 0:
                    self.menu_index = 0
                self._up_lock = True
            elif not self.controls.up_button:
                self._up_lock = False

            if self.controls.down_button and not self._down_lock:
                self.menu_index += 1
                if self.menu_index > len(self.menu_items) - 1:
                    self.menu_index = len(self.menu_items) - 1
                self._down_lock = True
            elif not self.controls.down_button:
                self._down_lock = False
        elif self.weapon_shop_open:
            # Weapon Shop navigation
            if self.controls.up_button and not self._up_lock:
                self.weapon_shop_index -= 1
                if self.weapon_shop_index < 0:
                    self.weapon_shop_index = 0
                self._up_lock = True
            elif not self.controls.up_button:
                self._up_lock = False

            if self.controls.down_button and not self._down_lock:
                self.weapon_shop_index += 1
                if self.weapon_shop_index > len(self.weapon_shop_items) - 1:
                    self.weapon_shop_index = len(self.weapon_shop_items) - 1
                self._down_lock = True
            elif not self.controls.down_button:
                self._down_lock = False

            # SHOW DESCRIPTION IN TEXTBOX WHEN SELECTION CHANGES
            if self.weapon_shop_index != self.last_weapon_shop_index:
                item = self.weapon_shop_items[self.weapon_shop_index]
                self.textbox.show(self.weapon_shop_descriptions.get(item, item))
                self.last_weapon_shop_index = self.weapon_shop_index
        elif self.defense_shop_open:
            # Defense Shop navigation
            if self.controls.up_button and not self._up_lock:
                self.defense_shop_index -= 1
                if self.defense_shop_index < 0:
                    self.defense_shop_index = 0
                self._up_lock = True
            elif not self.controls.up_button:
                self._up_lock = False

            if self.controls.down_button and not self._down_lock:
                self.defense_shop_index += 1
                if self.defense_shop_index > len(self.defense_shop_items) - 1:
                    self.defense_shop_index = len(self.defense_shop_items) - 1
                self._down_lock = True
            elif not self.controls.down_button:
                self._down_lock = False

            # SHOW DESCRIPTION IN TEXTBOX WHEN SELECTION CHANGES
            if self.defense_shop_index != self.last_defense_shop_index:
                item = self.defense_shop_items[self.defense_shop_index]
                self.textbox.show(self.defense_shop_descriptions.get(item, item))
                self.last_defense_shop_index = self.defense_shop_index

        # OPEN SHOPS (Primary fire key = F)
        if not self.weapon_shop_open and not self.defense_shop_open:
            if self.controls.main_weapon_button and not self._f_lock:
                if self.menu_index == 0:
                    self.weapon_shop_open = True
                    self.last_weapon_shop_index = -1  # force first description show
                elif self.menu_index == 1:
                    self.defense_shop_open = True
                    self.last_defense_shop_index = -1  # force first description show
                elif self.menu_index == 2:
                    # NEXT MISSION
                    state.starship.current_level += 1

                    # Save before transitioning
                    self.save_state.capture_player(state.starship)
                    self.save_state.save_to_file("player_save.json")

                    level_num = state.starship.current_level

                    # Import mapping and screens
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

                    from ScreenClasses.MissionBriefingScreenLevelOne import MissionBriefingScreenLevelOne
                    from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
                    from ScreenClasses.MissionBriefingScreenLevelThree import MissionBriefingScreenLevelThree
                    from ScreenClasses.MissionBriefingScreenLevelFour import MissionBriefingScreenLevelFour
                    from ScreenClasses.MissionBriefingScreenLevelFive import MissionBriefingScreenLevelFive

                    LEVEL_MAP_ACTUAL = {
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

                    LEVEL_MAP_BRIEFING = {
                        1: MissionBriefingScreenLevelOne,
                        2: MissionBriefingScreenLevelTwo,
                        3: MissionBriefingScreenLevelThree,
                        4: MissionBriefingScreenLevelFour,
                        5: MissionBriefingScreenLevelFive,
                    }

                    if self.show_mission_briefing and level_num in LEVEL_MAP_BRIEFING:
                        level_class = LEVEL_MAP_BRIEFING[level_num]
                    else:
                        level_class = LEVEL_MAP_ACTUAL.get(level_num, LevelOne)

                    if level_class in [
                        MissionBriefingScreenLevelOne,
                        MissionBriefingScreenLevelTwo,
                        MissionBriefingScreenLevelThree,
                        MissionBriefingScreenLevelFour,
                        MissionBriefingScreenLevelFive
                    ]:
                        state.currentScreen = level_class()
                    else:
                        state.currentScreen = level_class(state.textbox)

                    state.currentScreen.start(state)
                    return
                elif self.menu_index == 3:
                    # SAVE GAME
                    self.save_state.set_location_home_base()
                    self.save_state.capture_player(state.starship)
                    self.save_state.save_to_file("player_save.json")
                    self.textbox.show("Game saved.")
                elif self.menu_index == 4:
                    # LOAD GAME
                    if self.save_state.load_from_file("player_save.json"):
                        self.save_state.restore_player(state.starship)
                        self.textbox.show("Game loaded.")
                    else:
                        self.textbox.show("No save file found.")
                self._f_lock = True
            elif not self.controls.main_weapon_button:
                self._f_lock = False
        elif self.weapon_shop_open:
            # PURCHASE LOGIC (Primary fire key = F) while shop is open
            if self.controls.main_weapon_button and not self._f_lock:
                item = self.weapon_shop_items[self.weapon_shop_index]
                price = self.item_prices.get(item, 5000)
                if item not in state.starship.upgrade_chips:
                    if state.starship.money >= price:
                        state.starship.money -= price
                        state.starship.upgrade_chips.append(item)
                        if item == "Metal Shield":
                            state.starship.magic_inventory.append(item)
                            state.starship.equipped_magic[0] = item
                        elif item == "Wind Slicer":
                            state.starship.magic_inventory.append(item)
                            state.starship.equipped_magic[0] = item
                        elif item == "M. gun damage booster":
                            state.starship.machine_gun_damage += 0.1
                            print("I bought better bullets")
                        elif item == "Missile speed booster":
                            state.starship.missile_bullet_speed += 1.0
                            print("I bought better speed for missiles")
                        elif item == "Missile Count +1":
                            state.starship.missile.max_missiles += 1
                            print("I bought more missiles")

                        if hasattr(state.starship, "apply_upgrades"):
                            state.starship.apply_upgrades()
                        # Auto-save after successful purchase
                        self.save_state.set_location_home_base()
                        self.save_state.capture_player(state.starship)
                        self.save_state.save_to_file("player_save.json")
                        self.textbox.show(f"Purchased {item} for {price}!")
                    else:
                        self.textbox.show(f"Not enough money for {item} (Need {price}).")
                else:
                    self.textbox.show(f"{item} is already sold out.")
                self._f_lock = True
            elif not self.controls.main_weapon_button:
                self._f_lock = False
        elif self.defense_shop_open:
            # PURCHASE LOGIC (Primary fire key = F) while shop is open
            if self.controls.main_weapon_button and not self._f_lock:
                item = self.defense_shop_items[self.defense_shop_index]
                price = self.item_prices.get(item, 5000)
                if item not in state.starship.upgrade_chips:
                    if state.starship.money >= price:
                        state.starship.money -= price
                        state.starship.upgrade_chips.append(item)
                        if item == "Armor Plating":
                            state.starship.shipHealth += 50
                            state.starship.shipHealthMax += 50
                            print("I bought better hull amount")
                        elif item == "Shield Generator":
                            state.starship.current_shield += 25
                            state.starship.max_shield += 25
                            print("I bought better shield amount")
                        elif item == "Ki Efficiency chip":
                            state.starship.player_ki += 25
                            state.starship.player_max_ki += 25
                            print("I bought better ki amount")
                        elif item == "Shield Charger":
                            state.starship.shield_system.recharge_rate_shield += 0.2
                            print("I bought faster shield recharge")
                        elif item == "Speed up":
                            state.starship.speed += 0.6
                            print("I bought more speed")

                        if hasattr(state.starship, "apply_upgrades"):
                            state.starship.apply_upgrades()

                        # Auto-save after successful purchase
                        self.save_state.set_location_home_base()
                        self.save_state.capture_player(state.starship)
                        self.save_state.save_to_file("player_save.json")
                        self.textbox.show(f"Purchased {item} for {price}!")
                    else:
                        self.textbox.show(f"Not enough money for {item} (Need {price}).")
                else:
                    self.textbox.show(f"{item} is already sold out.")
                self._f_lock = True
            elif not self.controls.main_weapon_button:
                self._f_lock = False

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

        # Money display (top right)
        money_text = f"Credits: {state.starship.money}"
        money_surf = self.money_font.render(money_text, True, (255, 255, 100))
        money_x = self.weapon_shop_rect.right - money_surf.get_width() - 20
        state.DISPLAY.blit(money_surf, (money_x, y))

        y += title_surf.get_height() + 20

        arrow_surf = self.menu_font.render(self.arrow_text, True, (255, 255, 255))
        arrow_x = x - arrow_surf.get_width() - self.arrow_gap

        for i, item in enumerate(self.weapon_shop_items):
            if i == self.weapon_shop_index:
                state.DISPLAY.blit(arrow_surf, (arrow_x, y))

            surf = item_font.render(item, True, (255, 255, 255))
            state.DISPLAY.blit(surf, (x, y))

            # Price display
            price = self.item_prices.get(item, 5000)
            price_text = "sold out" if item in state.starship.upgrade_chips else str(price)
            price_surf = item_font.render(price_text, True, (255, 255, 255))
            state.DISPLAY.blit(price_surf, (x + surf.get_width() + 50, y))

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

        # Money display (top right)
        money_text = f"Money: {state.starship.money}"
        money_surf = self.money_font.render(money_text, True, (255, 255, 100))
        money_x = self.defense_shop_rect.right - money_surf.get_width() - 20
        state.DISPLAY.blit(money_surf, (money_x, y))

        y += title_surf.get_height() + 20

        arrow_surf = self.menu_font.render(self.arrow_text, True, (255, 255, 255))
        arrow_x = x - arrow_surf.get_width() - self.arrow_gap

        for i, item in enumerate(self.defense_shop_items):
            if i == self.defense_shop_index:
                state.DISPLAY.blit(arrow_surf, (arrow_x, y))

            surf = item_font.render(item, True, (255, 255, 255))
            state.DISPLAY.blit(surf, (x, y))

            # Price display
            price = self.item_prices.get(item, 5000)
            price_text = "sold out" if item in state.starship.upgrade_chips else str(price)
            price_surf = item_font.render(price_text, True, (255, 255, 255))
            state.DISPLAY.blit(price_surf, (x + surf.get_width() + 50, y))

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
