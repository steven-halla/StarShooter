import pygame
from Controller.KeyBoardControls import KeyBoardControls


class ShopKeeper:
    def __init__(self, textbox):
        self.textbox = textbox
        self.controls = KeyBoardControls()

        # layout config
        self.box_size = 32
        self.box_spacing = 40
        self.num_rows = 5
        self.num_cols = 5

        # purchase holding timer
        self.fill_timer = 0.0
        self.fill_target_time = 2000.0  # 2 seconds in milliseconds

        # top-left anchor for the vertical stack
        self.start_x = 60
        self.start_y = 90

        # spacing between columns
        self.column_spacing = 155

        # text layout
        # self.text_offset_x is no longer used for item names as they are centered on lines

        # colors
        self.box_color = (60, 60, 60)
        self.box_border_color = (255, 255, 255)
        self.selected_box_color = (0, 200, 0) # Highlight green
        self.line_color = (200, 200, 200)
        self.text_color = (220, 220, 220)

        # font
        self.font = pygame.font.Font(None, 24)

        # item names (RIGHT of boxes)
        # Organized as [Column 1 items, Column 2 items]
        self.item_names = [
            "DBL Barrel",
            "Quick Shot",
            "Atk Up +2",
            "ROF UP",
            "Atk Up +1",
            "Quick Charge",
            "Count +2",
            "Spd Boosters",
            "+100 damage",
            "Count +1",
            "Post Hit +",
            "Mv Speed +1",
            "HP + 25",
            "Mv Speed + 1",
            "HP + 25",
            "Quick Charge",
            "Shield + 50",
            "Rech Time +",
            "Rate Charge +",
            "Shields+ 50",
            "Ki + 25",
            "Wpn Chip ",
            "Wpn Chip ",
            "Wpn Chip ",
            "Ki Max + 25"
        ]

        # Calculate prices based on tier (row)
        # Bottom tier (row 4) is 1000, then 3000 for tier 2 (row 3)...
        # Pattern: 1000, 3000, 5000, 7000, 9000
        # Tiers are rows from bottom to top: 0=9000, 1=7000, 2=5000, 3=3000, 4=1000
        self.item_prices = []
        for c in range(self.num_cols):
            for r in range(self.num_rows):
                price = 1000 + (4 - r) * 2000
                self.item_prices.append(price)

        self.current_selected_chip = 0

        # dummy descriptions for textbox
        self.item_descriptions = [
            "Adds a second barrel.\nFires two bullets at once.",
            "Increases bullet speed by +1.\nShots travel faster.",
            "Increases weapon damage by 2 levels.",
            "Improves fire rate.\nShoot more often.",
            "Minor damage increase.\nCheap but effective.",
            "Decreases missile reload time.\nFire more frequently.",
            "Increases missile count by 2.\nLaunch a bigger volley.",
            "Increases missile flight speed.\nTargets have less time to react.",
            "Massive damage boost for missiles.\nDestroys heavy targets.",
            "Increases missile count by 1.\nSlightly larger volley.",
            "Increases post-hit invincibility by 0.5s.\nStay safe longer after being hit.",
            "Increases ship movement speed by 1.\nBe more agile.",
            "Increases ship max HP by 25.\nTake more hits.",
            "Further increases ship movement speed by 1.\nMaximum agility.",
            "Further increases ship max HP by 25.\nUltimate durability.",
            "Increases shield charge rate by 1.\nShield recovers faster.",
            "Increases maximum shield by 50.\nAbsorb more damage.",
            "Decreases shield recharge delay by 1.\nShield starts recovering sooner.",
            "Further increases shield charge rate by 1.\nRapid shield recovery.",
            "Further increases maximum shield by 50.\nMaximum shield capacity.",
            "Increases your maximum Ki points by 25.\nAllows for more special moves.",
            "Unlock a new weapon chip for your sub-weapons.\nExpand your arsenal.",
            "Unlock another weapon chip.\nMore power for your weapons.",
            "Unlock yet another weapon chip.\nMaximum versatility.",
            "Further increases your max Ki by 25.\nPeak energy capacity."
        ]

        self.item_chips = [
            "machine_gun_extra_bullet",
            "machine_gun_bullet_speed_up",
            "bullet_attack_up_plus_five",  # Actually level 2 is mapped to +5 in apply_upgrades
            "machine_gun_rate_of_fire_up",
            "bullet_attack_up_plus_five",  # This is a bit redundant but matches names
            "missile_regen_faster",
            "max_missiles_plus_two",
            "missile_bullet_speed_up",
            "missile_attack_up_plus_ten",
            "max_missiles_plus_two", # More missiles + 1?
            "post_hit_invincibility_plus_half",
            "ship_speed_plus_one",
            "ship_hp_plus_twenty_five",
            "ship_speed_plus_one",
            "ship_hp_plus_twenty_five",
            "shield_charge_rate_plus_one",
            "shield_max_plus_fifty",
            "shield_recharge_timer_plus_one",
            "shield_charge_rate_plus_one",
            "shield_max_plus_fifty",
            "ki_max_plus_twenty_five",
            "weapon_chip_upgrade",
            "weapon_chip_upgrade",
            "weapon_chip_upgrade",
            "ki_max_plus_twenty_five"
        ]

        # precompute box rects
        self.boxes: list[pygame.Rect] = []
        self.build_boxes()

    def start(self, state):
        # Always show current selected item description
        self.textbox.show(self._get_description(state, self.current_selected_chip))

    def _get_description(self, state, index):
        money_line = f"Money: {state.starship.money}"
        desc = self.item_descriptions[index]
        return f"{money_line}\n \n{desc}"

    def update(self, state):
        self.controls.update()
        if self.controls.isExitPressed:
            state.isRunning = False

        row = self.current_selected_chip % self.num_rows
        col = self.current_selected_chip // self.num_rows

        if self.controls.up_button:
            if row > 0:
                self.current_selected_chip -= 1
                self.textbox.show(self._get_description(state, self.current_selected_chip))
            self.controls.isUpPressed = False

        if self.controls.down_button:
            if row < self.num_rows - 1:
                self.current_selected_chip += 1
                self.textbox.show(self._get_description(state, self.current_selected_chip))
            self.controls.isDownPressed = False

        if self.controls.left_button:
            if col > 0:
                self.current_selected_chip -= self.num_rows
                self.textbox.show(self._get_description(state, self.current_selected_chip))
            self.controls.isLeftPressed = False

        if self.controls.right_button:
            if col < self.num_cols - 1:
                self.current_selected_chip += self.num_rows
                self.textbox.show(self._get_description(state, self.current_selected_chip))
            self.controls.isRightPressed = False

        if self.controls.main_weapon_button:
            self.fill_timer += state.delta
            if self.fill_timer >= self.fill_target_time:
                price = self.item_prices[self.current_selected_chip]
                chip_id = self.item_chips[self.current_selected_chip]
                if chip_id not in state.starship.upgrade_chips:
                    if state.starship.money >= price:
                        state.starship.money -= price
                        state.starship.upgrade_chips.append(chip_id)
                        state.starship.apply_upgrades()
                        print(f"Purchased chip: {chip_id} for {price}")
                        # Refresh textbox to show updated money
                        self.textbox.show(self._get_description(state, self.current_selected_chip))
                    else:
                        print(f"Not enough money for {chip_id}. Need {price}, have {state.starship.money}")
                self.fill_timer = 0.0 # reset after purchase
        else:
            self.fill_timer = 0.0

        if self.controls.qJustPressed:
            self.controls.qJustPressed = False

    def build_boxes(self) -> None:
        self.boxes.clear()

        for c in range(self.num_cols):
            for r in range(self.num_rows):
                x = self.start_x + c * self.column_spacing
                y = self.start_y + r * (self.box_size + self.box_spacing)
                rect = pygame.Rect(
                    x,
                    y,
                    self.box_size,
                    self.box_size
                )
                self.boxes.append(rect)

    def draw(self, state) -> None:
        state.DISPLAY.fill((0, 0, 0))

        # Draw money bar at top
        money_bar_height = 40
        pygame.draw.rect(state.DISPLAY, (0, 0, 0), (0, 0, state.DISPLAY.get_width(), money_bar_height))
        
        # Render and draw player money
        money_text = f"Money: ${state.starship.money}"
        money_surf = self.font.render(money_text, True, (255, 255, 255))
        money_rect = money_surf.get_rect(midleft=(20, money_bar_height // 2))
        state.DISPLAY.blit(money_surf, money_rect)

        self.draw_boxes(state.DISPLAY)
        self.draw_connecting_lines(state.DISPLAY)
        # Names are now drawn by draw_connecting_lines or a modified draw_item_names
        self.draw_item_names(state.DISPLAY)

        if self.textbox.is_visible():
            self.textbox.draw(state.DISPLAY)

        pygame.display.flip()

    # --------------------------------------------------
    # DRAW HELPERS
    # --------------------------------------------------

    def draw_boxes(self, display: pygame.Surface) -> None:
        for i, rect in enumerate(self.boxes):
            border_color = self.box_border_color
            if i == self.current_selected_chip:
                border_color = self.selected_box_color

            pygame.draw.rect(display, self.box_color, rect)

            # draw fill if selected
            if i == self.current_selected_chip and self.fill_timer > 0:
                fill_height = int((self.fill_timer / self.fill_target_time) * self.box_size)
                if fill_height > self.box_size:
                    fill_height = self.box_size
                fill_rect = pygame.Rect(rect.x, rect.y + rect.height - fill_height, rect.width, fill_height)
                pygame.draw.rect(display, (0, 255, 0), fill_rect)

            pygame.draw.rect(display, border_color, rect, 2)

    def draw_connecting_lines(self, display: pygame.Surface) -> None:
        for c in range(self.num_cols):
            for r in range(self.num_rows - 1):
                idx = c * self.num_rows + r
                top_rect = self.boxes[idx]
                bottom_rect = self.boxes[idx + 1]

                pygame.draw.line(
                    display,
                    self.line_color,
                    (top_rect.centerx, top_rect.bottom),
                    (bottom_rect.centerx, bottom_rect.top),
                    2
                )

    def draw_item_names(self, display: pygame.Surface) -> None:
        # Define column headers
        headers = ["Gun", "Missile", "Ship", "Shield", "Ki"]

        for c in range(self.num_cols):
            # Draw Column Header
            if c < len(headers):
                header_surf = self.font.render(headers[c], True, (255, 255, 100))
                first_rect = self.boxes[c * self.num_rows]
                header_rect = header_surf.get_rect(center=(first_rect.centerx, first_rect.top - 40))
                display.blit(header_surf, header_rect)

            for r in range(self.num_rows):
                idx = c * self.num_rows + r
                rect = self.boxes[idx]

                # Render name
                text_content = f"{self.item_names[idx]}"
                text_surf = self.font.render(
                    text_content,
                    True,
                    self.text_color
                )

                if r == 0:
                    # For the first item in each column, put it ABOVE the box
                    text_rect = text_surf.get_rect(center=(rect.centerx, rect.top - 20))
                else:
                    # For subsequent items, put them on the line ABOVE them (between r-1 and r)
                    prev_rect = self.boxes[idx - 1]
                    mid_y = (prev_rect.bottom + rect.top) // 2
                    text_rect = text_surf.get_rect(center=(rect.centerx, mid_y))

                display.blit(text_surf, text_rect)
