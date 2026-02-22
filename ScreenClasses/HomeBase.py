import pygame
from ScreenClasses.Screen import Screen
from Constants.GlobalConstants import GlobalConstants
from Controller.KeyBoardControls import KeyBoardControls


class HomeBase(Screen):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox
        self._welcome_shown: bool = False

        # RIGHT SIDE RECT (100 wide, 500 high)
        display_w, display_h = pygame.display.get_surface().get_size()
        self.right_panel_rect = pygame.Rect(
            display_w - 170,                 # x (flush right)
            (display_h - 500) // 2,          # y (centered vertically)
            140,                             # width
            300                              # height
        )

    def start(self, state) -> None:
        super().start(state)

        if not self._welcome_shown:
            self.textbox.show("Welcome to your home base")
            self._welcome_shown = True

    def update(self, state):
        super().update(state)



        if not hasattr(self, "controls"):
            self.controls = KeyBoardControls()

        self.controls.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.textbox.advance()

    def draw(self, state):
        state.DISPLAY.fill(GlobalConstants.BLACK)

        # draw the rect with a thick border
        pygame.draw.rect(state.DISPLAY, (255, 255, 255), self.right_panel_rect, 4)

        self.textbox.draw(state.DISPLAY)

        pygame.display.flip()
