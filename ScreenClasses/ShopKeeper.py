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

        # text layout
        self.text_offset_x = 60  # space to the right of the box

        # colors
        self.box_color = (60, 60, 60)
        self.box_border_color = (255, 255, 255)
        self.line_color = (200, 200, 200)
        self.text_color = (220, 220, 220)

        # font
        self.font = pygame.font.Font(None, 24)

        # item names (RIGHT of boxes)
        self.item_names = [
            "Double Barrel",
            "Faster Bullet",
            "Damage + Level 2",
            "Fire Rate Up",
            "Damage + Level 1",
        ]

        # dummy descriptions for textbox
        self.item_descriptions = [
            "Adds a second barrel.\nFires two bullets at once.",
            "Increases bullet speed by +1.\nShots travel faster.",
            "Increases weapon damage by 2 levels.",
            "Improves fire rate.\nShoot more often.",
            "Minor damage increase.\nCheap but effective.",
        ]

        # precompute box rects
        self.boxes: list[pygame.Rect] = []
        self.build_boxes()

    def start(self, state):
        # dummy: always show first item description for now
        self.textbox.show(self.item_descriptions[0])

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
        state.DISPLAY.fill((0, 0, 0))

        self.draw_boxes(state.DISPLAY)
        self.draw_connecting_lines(state.DISPLAY)
        self.draw_item_names(state.DISPLAY)

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

            pygame.draw.line(
                display,
                self.line_color,
                (top_rect.centerx, top_rect.bottom),
                (bottom_rect.centerx, bottom_rect.top),
                2
            )

    def draw_item_names(self, display: pygame.Surface) -> None:
        for i, rect in enumerate(self.boxes):
            text_surf = self.font.render(
                self.item_names[i],
                True,
                self.text_color
            )
            display.blit(
                text_surf,
                (rect.right + self.text_offset_x, rect.centery - text_surf.get_height() // 2)
            )
