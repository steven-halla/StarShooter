import pygame

from ScreenClasses.Screen import Screen
from Constants.GlobalConstants import GlobalConstants


class MissionBriefingScreenLevelOne(Screen):
    def __init__(self):
        super().__init__()
        self.font_title = pygame.font.Font(None, 48)
        self.font_body = pygame.font.Font(None, 26)
        self.set_player = "None"
        self.skip_ready_time = pygame.time.get_ticks() + 2500

        self.briefing_text = [
            "Mission Briefing: Destroy the hive",
            "",
            "We have  located a hidden hive of the undead legion.",
            "Your mission is to go in and destroy this hive before it increases in size",
            "Destroy all transport worms",
            "",
            "Collapse the worms and burn their cargo out with NAPALM",
            "If 4 worms survive we will have to recall the entire mission",
            "",
            "Slavers will come to order the worms to burrow, destroy them beforehand!",
            "",
            "Press F to deploy."
        ]

    def update(self, state):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                if pygame.time.get_ticks() < self.skip_ready_time:
                    return
                from Levels.LevelFour import LevelFour

                next_level = LevelFour()
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
