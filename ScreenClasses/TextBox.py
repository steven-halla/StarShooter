import pygame


class TextBox:
    """
    Bottom-screen RPG text box with portrait box.

    - Supports 3 lines per page
    - Pages are precomputed (index-based)
    - Typewriter effect (1 character at a time)
    - Q: finish typing → advance page → close
    """

    MAX_LINES_PER_PAGE = 3
    LINE_SPACING = 10

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        height: int = 140,
        bottom_offset: int = 20,
        font_size: int = 32,
        padding: int = 15,
        portrait_width: int = 150,
        gap: int = 15,
    ) -> None:

        self.padding = padding

        # ─────────────────────────────
        # POSITIONING
        # ─────────────────────────────
        self.base_x = 20
        self.y = screen_height - bottom_offset - height

        self.portrait_rect = pygame.Rect(
            self.base_x,
            self.y,
            portrait_width,
            height,
        )

        text_width = screen_width - self.base_x - portrait_width - gap - 20
        self.rect = pygame.Rect(
            self.base_x + portrait_width + gap,
            self.y,
            text_width,
            height,
        )

        # ─────────────────────────────
        # RENDERING
        # ─────────────────────────────
        self.font = pygame.font.Font(None, font_size)
        self.bg_color = (0, 0, 0)
        self.border_color = (255, 255, 255)
        self.text_color = (255, 255, 255)

        # ─────────────────────────────
        # STATE (INDEX-BASED)
        # ─────────────────────────────
        self.visible: bool = False
        self.pages: list[list[str]] = []
        self.page_index: int = 0

        # typewriter state
        self.is_typing: bool = False
        self.visible_chars: int = 0
        self.last_char_time: int = 0
        self.char_delay_ms: int = 30

    # ─────────────────────────────
    # VISIBILITY / CONTROL
    # ─────────────────────────────
    def show(self, text: str) -> None:
        self.pages = self._build_pages(text)
        self.page_index = 0
        self.visible = True

        # typing reset
        self.is_typing = True
        self.visible_chars = 0
        self.last_char_time = pygame.time.get_ticks()

    def hide(self) -> None:
        self.visible = False
        self.pages.clear()
        self.page_index = 0
        self.is_typing = False

    def is_visible(self) -> bool:
        return self.visible

    def advance(self) -> None:
        """
        Called when Q is pressed.
        """
        if self.is_typing:
            # finish current page instantly
            self.is_typing = False
            return

        if self.page_index < len(self.pages) - 1:
            self.page_index += 1
            self.is_typing = True
            self.visible_chars = 0
            self.last_char_time = pygame.time.get_ticks()
        else:
            self.hide()

    # ─────────────────────────────
    # DRAW
    # ─────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible or not self.pages:
            return

        pygame.draw.rect(surface, self.bg_color, self.portrait_rect)
        pygame.draw.rect(surface, self.border_color, self.portrait_rect, 2)

        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        self._draw_current_page(surface)

    # ─────────────────────────────
    # PAGE RENDERING
    # ─────────────────────────────
    def _draw_current_page(self, surface: pygame.Surface) -> None:
        x = self.rect.x + self.padding
        y = self.rect.y + self.padding

        _, line_height = self.font.size(" ")

        # flatten page into one string
        page_lines = self.pages[self.page_index]
        full_text = "\n".join(page_lines)

        visible_text = self._update_typing(full_text)
        visible_lines = visible_text.split("\n")

        for line in visible_lines:
            surface.blit(
                self.font.render(line, True, self.text_color),
                (x, y),
            )
            y += line_height + self.LINE_SPACING

    # ─────────────────────────────
    # PAGE BUILDING (ONE TIME)
    # ─────────────────────────────
    def _build_pages(self, text: str) -> list[list[str]]:
        input_lines = text.split("\n")
        space_width = self.font.size(" ")[0]
        max_width = self.rect.width - self.padding * 2

        wrapped_lines: list[str] = []
        for input_line in input_lines:
            words = input_line.split(" ")
            current_line = ""
            current_width = 0

            for word in words:
                word_width = self.font.size(word)[0]

                if current_width + word_width <= max_width:
                    current_line += word + " "
                    current_width += word_width + space_width
                else:
                    wrapped_lines.append(current_line.rstrip())
                    current_line = word + " "
                    current_width = word_width + space_width

            if current_line:
                wrapped_lines.append(current_line.rstrip())

        pages: list[list[str]] = []
        for i in range(0, len(wrapped_lines), self.MAX_LINES_PER_PAGE):
            pages.append(wrapped_lines[i:i + self.MAX_LINES_PER_PAGE])

        return pages

    # ─────────────────────────────
    # TYPEWRITER LOGIC
    # ─────────────────────────────
    def _update_typing(self, full_text: str) -> str:
        if not self.is_typing:
            return full_text

        now = pygame.time.get_ticks()

        if now - self.last_char_time >= self.char_delay_ms:
            self.visible_chars += 1
            self.last_char_time = now

            if self.visible_chars >= len(full_text):
                self.visible_chars = len(full_text)
                self.is_typing = False

        return full_text[:self.visible_chars]
