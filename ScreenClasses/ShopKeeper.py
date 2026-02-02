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
        self.num_cols = 4

        # top-left anchor for the vertical stack
        self.start_x = 80
        self.start_y = 90

        # spacing between columns
        self.column_spacing = 150

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
            "Double Barrel",
            "Faster Bullet",
            "Damage + Level 2",
            "Fire Rate Up",
            "Damage + Level 1",
            "Faster Recharge",
            "More Missiles + 2",
            "Faster Missile",
            "Damage + 100",
            "More Missiles + 1",
            "Post Hit Invincibility",
            "Ship Speed + 1",
            "Ship HP + 25",
            "Ship Speed + 1",
            "Ship HP + 25",
            "Faster Rate Charge + 1",
            "Shields Max + 50",
            "Faster Recharge Timer + 1",
            "Faster Rate Charge + 1",
            "Shields Max + 50"
        ]

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
            "Further increases maximum shield by 50.\nMaximum shield capacity."
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
            "shield_max_plus_fifty"
        ]

        # precompute box rects
        self.boxes: list[pygame.Rect] = []
        self.build_boxes()

    def start(self, state):
        # Always show current selected item description
        self.textbox.show(self.item_descriptions[self.current_selected_chip])

    def update(self, state):
        self.controls.update()
        if self.controls.isExitPressed:
            state.isRunning = False

        row = self.current_selected_chip % self.num_rows
        col = self.current_selected_chip // self.num_rows

        if self.controls.up_button:
            if row > 0:
                self.current_selected_chip -= 1
                self.textbox.show(self.item_descriptions[self.current_selected_chip])
            self.controls.isUpPressed = False

        if self.controls.down_button:
            if row < self.num_rows - 1:
                self.current_selected_chip += 1
                self.textbox.show(self.item_descriptions[self.current_selected_chip])
            self.controls.isDownPressed = False

        if self.controls.left_button:
            if col > 0:
                self.current_selected_chip -= self.num_rows
                self.textbox.show(self.item_descriptions[self.current_selected_chip])
            self.controls.isLeftPressed = False

        if self.controls.right_button:
            if col < self.num_cols - 1:
                self.current_selected_chip += self.num_rows
                self.textbox.show(self.item_descriptions[self.current_selected_chip])
            self.controls.isRightPressed = False

        if self.controls.qJustPressed:
            chip_id = self.item_chips[self.current_selected_chip]
            if chip_id not in state.starship.upgrade_chips:
                state.starship.upgrade_chips.append(chip_id)
                state.starship.apply_upgrades()
                print(f"Purchased chip: {chip_id}")
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
            color = self.box_color
            if i == self.current_selected_chip:
                color = self.selected_box_color

            pygame.draw.rect(display, color, rect)
            pygame.draw.rect(display, self.box_border_color, rect, 2)

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
        for c in range(self.num_cols):
            for r in range(self.num_rows):
                idx = c * self.num_rows + r
                rect = self.boxes[idx]

                # Render name
                text_surf = self.font.render(
                    self.item_names[idx],
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
