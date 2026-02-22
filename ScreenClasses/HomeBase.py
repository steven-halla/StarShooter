import pygame
from ScreenClasses.Screen import Screen
from Constants.GlobalConstants import GlobalConstants
from Controller.KeyBoardControls import KeyBoardControls


class HomeBase(Screen):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox
        self._welcome_shown: bool = False

        # background image (top portion)
        self.hangerbay_image = pygame.image.load("Assets/Images/hangerbay.png").convert()

        # RIGHT SIDE RECT
        display_w, display_h = pygame.display.get_surface().get_size()
        self.right_panel_rect = pygame.Rect(
            display_w - 175,
            (display_h - 500) // 2,
            150,
            325
        )

        # menu text
        self.menu_font = pygame.font.SysFont("arial", 20)
        self.menu_items: list[str] = ["W. Shop", "D. Shop", "N. Mission"]
        self.menu_padding_x: int = 45
        self.menu_padding_y: int = 16
        self.menu_line_gap: int = 14

        self.upper_padding: int = 12

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

    def draw_upper_home_base_screen(self, state) -> None:
        text_box_rect = self.textbox.rect

        top_area = pygame.Rect(
            0,
            0,
            state.DISPLAY.get_width(),
            max(0, text_box_rect.top - self.upper_padding)
        )

        if top_area.height <= 0:
            return

        img_w, img_h = self.hangerbay_image.get_size()
        scale = min(top_area.width / img_w, top_area.height / img_h)

        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        scaled = pygame.transform.scale(self.hangerbay_image, (new_w, new_h))

        x = top_area.x + (top_area.width - new_w) // 2 - 100
        y = top_area.y + (top_area.height - new_h) // 2

        state.DISPLAY.blit(scaled, (x, y))

    def draw(self, state):
        state.DISPLAY.fill(GlobalConstants.BLACK)

        self.draw_upper_home_base_screen(state)

        # box
        pygame.draw.rect(state.DISPLAY, (255, 255, 255), self.right_panel_rect, 4)

        # text inside box
        x = self.right_panel_rect.x + self.menu_padding_x
        y = self.right_panel_rect.y + self.menu_padding_y
        for item in self.menu_items:
            surf = self.menu_font.render(item, True, (255, 255, 255))
            state.DISPLAY.blit(surf, (x, y))
            y += surf.get_height() + self.menu_line_gap

        self.textbox.draw(state.DISPLAY)

        pygame.display.flip()
