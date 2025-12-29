import pygame


class TextBox:
    """
    A bottom-screen RPG-style text box.

    - Always anchored to the bottom of the screen
    - Renders ABOVE everything else (must be drawn last)
    - Black background with white border
    - Supports multi-line wrapped text
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        height: int = 140,
        bottom_offset: int = 20,
        font_size: int = 24,
        padding: int = 12,
    ) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.height = height
        self.bottom_offset = bottom_offset
        self.padding = padding

        self.font = pygame.font.Font(None, font_size)

        self.visible: bool = False
        self.text: str = ""

        self.rect = pygame.Rect(
            0,
            self.screen_height - self.bottom_offset - self.height,
            self.screen_width,
            self.height,
        )

        self.bg_color = (0, 0, 0)
        self.border_color = (255, 255, 255)
        self.text_color = (255, 255, 255)

    # -------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------
    def show(self, text: str) -> None:
        self.text = text
        self.visible = True

    def hide(self) -> None:
        self.visible = False
        self.text = ""

    def is_visible(self) -> bool:
        return self.visible

    # -------------------------------------------------
    # DRAW (CALL LAST, ALWAYS)
    # -------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        # background
        pygame.draw.rect(surface, self.bg_color, self.rect)

        # border
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        # text
        self._draw_text(surface)

    # -------------------------------------------------
    # INTERNAL
    # -------------------------------------------------
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
                line_surface = self.font.render(" ".join(current_line), True, self.text_color)
                surface.blit(line_surface, (x, y))
                y += line_height + 4
                current_line = [word]
                current_width = word_width + space_width

        if current_line:
            line_surface = self.font.render(" ".join(current_line), True, self.text_color)
            surface.blit(line_surface, (x, y))
