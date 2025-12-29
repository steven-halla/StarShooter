import pygame


class TextBox:
    """
    Bottom-screen RPG text box with portrait box.

    - Both boxes move together
    - Drawn last
    - One coordinate system (base_x)
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        height: int = 140,
        bottom_offset: int = 20,
        font_size: int = 24,
        padding: int = 12,
        portrait_width: int = 150,
        gap: int = 10,
    ) -> None:

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.height = height
        self.bottom_offset = bottom_offset
        self.padding = padding

        # ─────────────────────────────
        # SINGLE SOURCE OF TRUTH
        # Move this to move BOTH boxes
        # ─────────────────────────────
        self.base_x = 70
        self.y = screen_height - bottom_offset - height

        # ─────────────────────────────
        # PORTRAIT BOX
        # ─────────────────────────────
        self.portrait_rect = pygame.Rect(
            self.base_x,
            self.y,
            portrait_width,
            height,
        )

        # ─────────────────────────────
        # MAIN TEXT BOX
        # ─────────────────────────────
        text_width = screen_width - self.base_x - portrait_width - gap - 20

        self.rect = pygame.Rect(
            self.base_x + portrait_width + gap,
            self.y,
            text_width,
            height,
        )

        # rendering
        self.font = pygame.font.Font(None, font_size)
        self.bg_color = (0, 0, 0)
        self.border_color = (255, 255, 255)
        self.text_color = (255, 255, 255)

        self.visible = False
        self.text = ""

    # ─────────────────────────────
    # VISIBILITY
    # ─────────────────────────────
    def show(self, text: str) -> None:
        self.text = text
        self.visible = True

    def hide(self) -> None:
        self.text = ""
        self.visible = False

    def is_visible(self) -> bool:
        return self.visible

    # ─────────────────────────────
    # DRAW (CALL LAST, EVERY FRAME)
    # ─────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        # portrait box
        pygame.draw.rect(surface, self.bg_color, self.portrait_rect)
        pygame.draw.rect(surface, self.border_color, self.portrait_rect, 2)

        # main text box
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        self._draw_text(surface)

    # ─────────────────────────────
    # TEXT WRAPPING
    # ─────────────────────────────
    def _draw_text(self, surface: pygame.Surface) -> None:
        words = self.text.split(" ")
        space_width, line_height = self.font.size(" ")

        max_width = self.rect.width - self.padding * 2
        x = self.rect.x + self.padding
        y = self.rect.y + self.padding

        current_line = []
        current_width = 0

        for word in words:
            word_surface = self.font.render(word, True, self.text_color)
            word_width = word_surface.get_width()

            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width + space_width
            else:
                surface.blit(
                    self.font.render(" ".join(current_line), True, self.text_color),
                    (x, y),
                )
                y += line_height + 4
                current_line = [word]
                current_width = word_width + space_width

        if current_line:
            surface.blit(
                self.font.render(" ".join(current_line), True, self.text_color),
                (x, y),
            )
