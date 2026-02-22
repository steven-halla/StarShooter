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
            "Mission Briefing: Save the colony",
            "",
            "The Space colony Beckersville is under attack from the undead legion.",
            "Ammo is almost depleted, and most of the barrels have melted.",
            "The enemy strike force includes a Harvester bio ship.",
            "",
            "Objectives:",
            "- Destroy at least 40 enemies.",
            "- Destroy the Harvester Bio ship.",
            "",
            "All fighter pilots are dead. You will be alone.",
            "",
            "Controls:",
            "- Arrow keys: Move",
            "- F: Machine gun fire",
            "- A: Launch missiles",
            "- D: Special attack",
            "",
            "Press F to deploy."
        ]

        self.briefing_message: str = "\n".join(self.briefing_text)
        self._briefing_shown: bool = False

        # portrait settings
        self.portrait_box_gap = 24

        # sprite sheet
        self.character_sprite_image = pygame.image.load(
            "Assets/Images/tarial_sixteen_bit_spirte_sheet.png"
        ).convert_alpha()

        # frame rect (LEFT frame only)
        # NOTE: this assumes your sheet is 3 frames across with the same height
        frame_w = self.character_sprite_image.get_width() // 3
        frame_h = self.character_sprite_image.get_height()

        # Use ints for subsurface rect
        self.portrait_sprite_rect = pygame.Rect(0, 0, int(frame_w), int(frame_h))

    def update(self, state):
        if not self._briefing_shown:
            state.textbox.show(self.briefing_message)
            self._briefing_shown = True

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    state.textbox.advance()

                if event.key == pygame.K_f:
                    if pygame.time.get_ticks() < self.skip_ready_time:
                        return
                    if state.textbox.is_visible():
                        return

                    from Levels.LevelOne import LevelOne
                    next_level = LevelOne(state.textbox)
                    next_level.set_player(state.starship)
                    state.currentScreen = next_level
                    next_level.start(state)
                    return

    def draw(self, state):
        state.DISPLAY.fill((0, 0, 0))

        state.textbox.draw(state.DISPLAY)

        text_box_rect = state.textbox.rect

        portrait_box_size = text_box_rect.height
        portrait_box_rect = pygame.Rect(
            text_box_rect.left - self.portrait_box_gap - portrait_box_size,
            text_box_rect.top,
            portrait_box_size,
            portrait_box_size
        )

        sprite_rect = pygame.Rect(60, 320, 440, 440)
        sprite = self.character_sprite_image.subsurface(sprite_rect)
        scaled_sprite = pygame.transform.scale(sprite, (portrait_box_rect.width, portrait_box_rect.height -10))
        sprite_x = portrait_box_rect.x
        sprite_y = portrait_box_rect.y
        state.DISPLAY.blit(scaled_sprite, (sprite_x +3, sprite_y +5))

        pygame.display.flip()
