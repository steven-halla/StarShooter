import pygame

from SaveStates.SaveState import SaveState
from ScreenClasses.Screen import Screen
from Constants.GlobalConstants import GlobalConstants


class MissionBriefingScreenLevelOne(Screen):
    def __init__(self):
        super().__init__()
        self.level_start:bool = True
        self.font_title = pygame.font.Font(None, 48)
        self.font_body = pygame.font.Font(None, 26)
        self.set_player = "None"
        self.skip_ready_time = pygame.time.get_ticks() + 2500
        self.save_state = SaveState()


        self.briefing_text = [
            "Mission Briefing: Save the colony",
            "",
            "The Space colony Beckersville  is under attack from the undead legion",
            "Ammo is almost depleted, and most of the barrels have melted.",
            "The enemy strike force includes a Harvester bio ship",
            "",
            "Destroy at least 40 enemies.",
            "Destroy the Harvester Bio ship",
            "",
            "All fighter pilots are deadk, you will be alone.",
            "",
            "Use arrow keys to move. Press F key Machine gun Fire..",
            "",
            "Press A key to launch missiles. Press D key to launch Special Attack",
            "",

            "Press F to deploy."
        ]

    def update(self, state):
        if self.level_start == True:
            self.level_start = False

            self.save_state.capture_player(state.starship)
            self.save_state.save_to_file("player_save.json")
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:

                if pygame.time.get_ticks() < self.skip_ready_time:
                    return
                from Levels.LevelOne import LevelOne

                next_level = LevelOne()
                next_level.set_player(state.starship)
                state.currentScreen = next_level
                next_level.start(state)
                return
    def draw(self, state):
        state.DISPLAY.fill((0, 0, 0))

        y = 80
        for i, line in enumerate(self.briefing_text):
            if i == 0:
                text_surface = self.font_title.render(line, True, (255, 50, 50))
            else:
                text_surface = self.font_body.render(line, True, (200, 200, 200))

            rect = text_surface.get_rect(
    center=(GlobalConstants.WINDOWS_SIZE[0] // 2, y)
)
            state.DISPLAY.blit(text_surface, rect)
            y += 36

        pygame.display.flip()
