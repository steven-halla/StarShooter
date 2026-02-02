import pygame
from Controller.KeyBoardControls import KeyBoardControls


class ShopKeeper:
    def __init__(self, textbox):
        self.textbox = textbox
        self.controls = KeyBoardControls()

        # layout config
        self.box_size = 32
        self.box_spacing = 40
        self.num_boxes = 5

        # top-left anchor for the vertical stack
        self.start_x = 100
        self.start_y = 120

        # colors
        self.box_color = (60, 60, 60)
        self.box_border_color = (255, 255, 255)
        self.line_color = (200, 200, 200)

        # precompute box rects
        self.boxes: list[pygame.Rect] = []
        self.build_boxes()

    def start(self, state):
        pass

    def update(self, state):
        self.controls.update()
        if self.controls.isExitPressed:
            state.isRunning = False

    def build_boxes(self) -> None:
        self.boxes.clear()

        for i in range(self.num_boxes):
            y = self.start_y + i * (self.box_size + self.box_spacing)
            rect = pygame.Rect(
                self.start_x,
                y,
                self.box_size,
                self.box_size
            )
            self.boxes.append(rect)

    def draw(self, state) -> None:
        state.DISPLAY.fill((0, 0, 0)) # Fill background
        self.draw_boxes(state.DISPLAY)
        self.draw_connecting_lines(state.DISPLAY)

        if self.textbox.is_visible():
            self.textbox.draw(state.DISPLAY)

        pygame.display.flip()

    # --------------------------------------------------
    # DRAW HELPERS
    # --------------------------------------------------

    def draw_boxes(self, display: pygame.Surface) -> None:
        for rect in self.boxes:
            pygame.draw.rect(display, self.box_color, rect)
            pygame.draw.rect(display, self.box_border_color, rect, 2)

    def draw_connecting_lines(self, display: pygame.Surface) -> None:
        for i in range(len(self.boxes) - 1):
            top_rect = self.boxes[i]
            bottom_rect = self.boxes[i + 1]

            start_pos = (
                top_rect.centerx,
                top_rect.bottom
            )
            end_pos = (
                bottom_rect.centerx,
                bottom_rect.top
            )

            pygame.draw.line(
                display,
                self.line_color,
                start_pos,
                end_pos,
                2
            )
