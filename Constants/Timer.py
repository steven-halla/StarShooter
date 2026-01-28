import pygame

class Timer:
    MS_PER_SECOND: int = 1000

    def __init__(self, interval_seconds: float) -> None:
        self.interval_ms: int = int(interval_seconds * self.MS_PER_SECOND)
        # start “ready” so first call can fire immediately
        self.last_time_ms: int = pygame.time.get_ticks() - self.interval_ms

    def reset(self) -> None:
        self.last_time_ms = pygame.time.get_ticks()

    def is_ready(self) -> bool:
        now: int = pygame.time.get_ticks()
        return now - self.last_time_ms >= self.interval_ms

        # -----------------------------
        # BASIC CONTROL
        # -----------------------------

    def start(self) -> None:
        if self.start_time_ms is None:
            self.start_time_ms = pygame.time.get_ticks()


    def stop(self) -> None:
        self.reset()

        # -----------------------------
        # PAUSE / RESUME
        # -----------------------------

    def pause(self) -> None:
        if not self.paused and self.start_time_ms is not None:
            self.paused = True
            self.pause_time_ms = pygame.time.get_ticks()

    def resume(self) -> None:
        if self.paused:
            now = pygame.time.get_ticks()
            paused_duration = now - self.pause_time_ms
            self.start_time_ms += paused_duration
            self.paused = False

        # -----------------------------
        # STATE QUERIES
        # -----------------------------

    def is_running(self) -> bool:
        return self.start_time_ms is not None and not self.paused

    def elapsed_ms(self) -> int:
        if self.start_time_ms is None:
            return 0
        if self.paused:
            return self.pause_time_ms - self.start_time_ms
        return pygame.time.get_ticks() - self.start_time_ms

    def elapsed_seconds(self) -> float:
        return self.elapsed_ms() / self.MS_PER_SECOND

    def remaining_ms(self) -> int:
        return max(0, self.interval_ms - self.elapsed_ms())

    def progress(self) -> float:
        """0.0 → 1.0"""
        if self.interval_ms == 0:
            return 1.0
        return min(1.0, self.elapsed_ms() / self.interval_ms)

    def is_expired(self) -> bool:
        return self.start_time_ms is not None and self.elapsed_ms() >= self.interval_ms
