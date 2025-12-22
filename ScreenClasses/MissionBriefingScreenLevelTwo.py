import pygame

from ScreenClasses.Screen import Screen
from Constants.GlobalConstants import GlobalConstants


class MissionBriefingScreenLevelTwo(Screen):
    def __init__(self):
        super().__init__()
        self.font_title = pygame.font.Font(None, 48)
        self.font_body = pygame.font.Font(None, 26)
        self.set_player = "None"

        self.briefing_text = [
            "MISSION BRIEFING: Escort the Commander",
            "",
            "Commander Du-point is needing escort to the outer sector.",
            "Pockets of Acid Gas are about, avoid this at all cost",
            "Your job is to safely escort the Commander.",
            "",
            "Enemies in this sector are  immune to the acid",
            "A Slaver bio ship is in the area, which is a high priority target",
            "",
            "The commanders life is of upmost imporants",
            "",
            "Press F to deploy."
        ]

    def update(self, state):
        for event in pygame.event.get():
            if event.key == pygame.K_f:
                from Levels.LevelTwo import LevelTwo

                next_level = LevelTwo()
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
