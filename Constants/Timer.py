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
