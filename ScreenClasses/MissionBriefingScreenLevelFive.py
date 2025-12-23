import pygame

from ScreenClasses.Screen import Screen
from Constants.GlobalConstants import GlobalConstants


class MissionBriefingScreenLevelFive(Screen):
    def __init__(self):
        super().__init__()
        self.font_title = pygame.font.Font(None, 48)
        self.font_body = pygame.font.Font(None, 26)
        self.set_player = "None"
        self.skip_ready_time = pygame.time.get_ticks() + 2500

        self.briefing_text = [
            "Mission Briefing: Rescue the civilians",
            "",
            "A civilian class deluxe luxury cruise liner was destroyed, their escape pods scattered.",
            "The undead legion has sent units to capture them alive",
            "Rescue the civilian and clear the way for our transport ships",
            "",
            "Friendly fire is active, do not hit the civilians",
            "You must rescue at least 7 escape pods.",
            "",
            "Watch out for radiation zones.",
            "",
            "Press F to deploy."
        ]

    def update(self, state):
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

            rect = text_surface.get_rect(center=(GlobalConstants.WINDOWS_SIZE[0] // 2, y))
            state.DISPLAY.blit(text_surface, rect)
            y += 36

        pygame.display.flip()
