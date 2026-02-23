import pygame

from SaveStates.SaveState import SaveState
from ScreenClasses.Screen import Screen


class MissionBriefingScreenLevelOne(Screen):
    def __init__(self):
        super().__init__()
        self.level_start: bool = True
        self.skip_ready_time = pygame.time.get_ticks() + 2500
        self.save_state = SaveState()

        self.briefing_text = [
            "The space port of bakarant is under attack by the undead legion, fighters have been scrambled and you are to assist.",
            "",

            "Ammo is almost depleted, and most of the space ports barrels have melted.",
            "The enemy strike force includes a Harvester bio ship.",
            "",

            "-Your objective is to  Destroy at least 40 enemies.",
            "- Destroy the Harvester Bio ship.",
            "You will be deployed in sector 243 333 433",
            "The reward for the mission is 5000 credits that you can use for upgrades",
            "",
            "Controls:",
            "- Arrow keys: Move",
            "- F: Machine gun fire",
            "- B: Launch missiles",
            "- D: Special attack",
            "",
            "Press F to deploy."
        ]

        self.briefing_message: str = "\n".join(self.briefing_text)
        self._briefing_shown: bool = False

        self.portrait_box_gap = 24

        self.character_sprite_image = pygame.image.load(
            "Assets/Images/tarial_sixteen_bit_spirte_sheet.png"
        ).convert_alpha()

        self.sprite_rect_1 = pygame.Rect(70, 320, 440, 440)
        self.sprite_rect_2 = pygame.Rect(510, 320, 480, 440)
        self.sprite_rect_3 = pygame.Rect(990, 320, 475, 440)

        self.sprite_rects: list[pygame.Rect] = [
            self.sprite_rect_1,
            self.sprite_rect_2,
            self.sprite_rect_3
        ]

        self.current_sprite_index: int = 0
        self.sprite_cycle_interval_ms: int = 300
        self.last_sprite_switch_time: int = pygame.time.get_ticks()

        # mission brief header image (top of screen)
        self.mission_brief_image = pygame.image.load(
            "Assets/Images/missionbrief.png"
        ).convert_alpha()
        self.mission_brief_padding_top = 16
        self.mission_brief_padding_side = 16

    def draw_upper_mission_brief_screen(self, state) -> None:
        text_box_rect = state.textbox.rect

        max_width = state.DISPLAY.get_width() - (self.mission_brief_padding_side * 2 )
        max_height = text_box_rect.top - self.mission_brief_padding_top

        if max_width <= 0 or max_height <= 0:
            return

        img_w = self.mission_brief_image.get_width()
        img_h = self.mission_brief_image.get_height()

        if img_w <= 0 or img_h <= 0:
            return

        scale = min(max_width / img_w, max_height / img_h, 1.0)
        new_w = int(img_w * scale + 230)
        new_h = int(img_h * scale +40)

        if new_w <= 0 or new_h <= 0:
            return

        scaled = pygame.transform.scale(self.mission_brief_image, (new_w, new_h))

        x = (state.DISPLAY.get_width() - new_w) // 2
        y = self.mission_brief_padding_top

        state.DISPLAY.blit(scaled, (x+20, y - 40))

    def _try_deploy(self, state) -> None:
        if pygame.time.get_ticks() < self.skip_ready_time:
            return
        if state.textbox.is_visible():
            return

        from Levels.LevelOne import LevelOne
        next_level = LevelOne(state.textbox)
        next_level.set_player(state.starship)
        state.currentScreen = next_level
        next_level.start(state)

    def update(self, state):
        super().update(state)

        if not self._briefing_shown:
            state.textbox.show(self.briefing_message)
            self._briefing_shown = True

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    state.textbox.advance()

                if event.key == pygame.K_f:
                    self._try_deploy(state)

    def draw(self, state):
        state.DISPLAY.fill((0, 0, 0))

        # NEW: draw the mission brief image above the textbox
        self.draw_upper_mission_brief_screen(state)

        state.textbox.draw(state.DISPLAY)

        now = pygame.time.get_ticks()
        if now - self.last_sprite_switch_time >= self.sprite_cycle_interval_ms:
            self.current_sprite_index = (self.current_sprite_index + 1) % len(self.sprite_rects)
            self.last_sprite_switch_time = now

        text_box_rect = state.textbox.rect

        portrait_box_size = text_box_rect.height
        portrait_box_rect = pygame.Rect(
            text_box_rect.left - self.portrait_box_gap - portrait_box_size,
            text_box_rect.top,
            portrait_box_size,
            portrait_box_size
        )

        sprite_rect = self.sprite_rects[self.current_sprite_index]
        sprite = self.character_sprite_image.subsurface(sprite_rect)
        scaled_sprite = pygame.transform.scale(
            sprite,
            (portrait_box_rect.width, portrait_box_rect.height - 10)
        )

        sprite_x = portrait_box_rect.x
        sprite_y = portrait_box_rect.y
        state.DISPLAY.blit(scaled_sprite, (sprite_x + 3, sprite_y + 5))

        pygame.display.flip()
