
# this class is important for positions
class Camera:
    def __init__(
        self,
        window_width: int,
        window_height: int,
        world_height: int,
        scroll_speed_per_frame: float = 2.0,
        initial_zoom: float = 1.0,
    ) -> None:
        # sizes
        self.window_width: int = window_width
        self.window_height: int = window_height
        self.world_height: int = world_height

        # start at bottom of the world
        self.y: float = float(self.world_height - self.window_height)
        self.scroll_speed_per_frame: float = scroll_speed_per_frame

        # zoom
        self.zoom: float = initial_zoom
        self.min_zoom: float = 1.0
        self.max_zoom: float = 4.0
        # start at left of the world
        self.x: float = 0.0

    # -------- camera movement (vertical) --------
    def scroll_up(self) -> None:
        new_y = self.y - self.scroll_speed_per_frame
        if new_y < 0.0:
            new_y = 0.0
        self.y = new_y

    # -------- zoom like that example --------
    def zoom_in(self, step: float = 0.1) -> None:
        self.zoom = min(self.max_zoom, self.zoom + step)
        print(f"Zoom IN -> {self.zoom:.2f}")

    def zoom_out(self, step: float = 0.1) -> None:
        self.zoom = max(self.min_zoom, self.zoom - step)
        print(f"Zoom OUT -> {self.zoom:.2f}")

    # -------- world → screen helpers (key pattern) --------
    def world_to_screen_x(self, world_x: float) -> float:
        # no horizontal camera yet, just zoom
        return world_x * self.zoom

    def world_to_screen_y(self, world_y: float) -> float:
        # same idea as their group: (world - camera) * zoom
        return (world_y - self.y) * self.zoom

    def get_world_x_left(self) -> float:
        """
        Returns the world-space X position at the left edge of the screen.
        Camera does not scroll horizontally, so this is always 0.
        """
        return 0.0
