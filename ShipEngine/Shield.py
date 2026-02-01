import pygame


class Shield:
    def __init__(
        self,
        max_shield_points: int,
        recharge_rate_shield: float,
        time_to_start_shield_recharge: int,
    ):
        self.max_shield_points: int = max_shield_points
        self.current_shield_points: float = max_shield_points

        self.recharge_rate_shield: float = recharge_rate_shield
        self.time_to_start_shield_recharge: int = time_to_start_shield_recharge

        self._last_damage_time: int = 0
        self._is_depleted: bool = False

    # -------------------------
    # DAMAGE HANDLING
    # -------------------------
    def take_damage(self, damage: float) -> float:
        """
        Applies damage to shield.
        Returns leftover damage if shield breaks.
        """
        if self.current_shield_points <= 0:
            return damage

        self._last_damage_time = pygame.time.get_ticks()

        self.current_shield_points -= damage

        if self.current_shield_points <= 0:
            leftover = abs(self.current_shield_points)
            self.current_shield_points = 0
            self._is_depleted = True
            return leftover

        return 0.0

    # -------------------------
    # UPDATE (CALL EVERY FRAME)
    # -------------------------
    def update(self) -> None:
        if self.current_shield_points >= self.max_shield_points:
            self._is_depleted = False
            return

        now = pygame.time.get_ticks()

        if now - self._last_damage_time < self.time_to_start_shield_recharge:
            return

        self.current_shield_points += self.recharge_rate_shield

        if self.current_shield_points >= self.max_shield_points:
            self.current_shield_points = self.max_shield_points
            self._is_depleted = False

    # -------------------------
    # HELPERS
    # -------------------------
    def is_active(self) -> bool:
        return self.current_shield_points > 0

    def is_full(self) -> bool:
        return self.current_shield_points >= self.max_shield_points

    def force_disable(self) -> None:
        self.current_shield_points = 0
        self._is_depleted = True

    def reset(self) -> None:
        self.current_shield_points = self.max_shield_points
        self._is_depleted = False
        self._last_damage_time = 0
