import pygame


from ScreenClasses.Screen import Screen
from Constants.GlobalConstants import GlobalConstants


class MissionBriefingScreenLevelThree(Screen):
    def __init__(self):
        super().__init__()
        self.font_title = pygame.font.Font(None, 48)
        self.font_body = pygame.font.Font(None, 26)
        self.set_player = "None"
        self.skip_ready_time = pygame.time.get_ticks() + 2500


        self.briefing_text = [
            "MISSION BRIEFING: Protect Star Base",
            "",
            "I am the Grand master General, I  will ride upon your ship",
            "You are to direct your ship to block incoming enemy fire. ",
            "I will deflect ALL projectiles, but I can't protect you from Mellee",
            "",
            "Your ships slow speed is of no consequence, go as fast as you need.",
            "I will take a pure defensive stance, you will need to provide fire support" 
            "",
            "A ship Cracker is in the area, be aware of it's presence.",
            "",
            "Press F to deploy."
        ]

    def update(self, state):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                if pygame.time.get_ticks() < self.skip_ready_time:
                    return
                from Levels.levelThree import LevelThree

                next_level = LevelThree()
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
