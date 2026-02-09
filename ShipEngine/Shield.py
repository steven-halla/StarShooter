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

        self.courtesy_invincibility_duration: int = 1000  # 0.5 seconds
        self._last_hit_time: int = -500
    # -------------------------
    # DAMAGE HANDLING
    # -------------------------
    def take_damage(self, damage: float) -> None:
        """
        Applies damage to shield.
        Any overflow damage is applied to owner.shipHealth.
        """
        print("taking damage")
        now = pygame.time.get_ticks()

        # Courtesy invincibility check
        if damage > 0:
            if now - self._last_hit_time < self.courtesy_invincibility_duration:
                return
            self._last_hit_time = now

        self._last_damage_time = now

        if self.current_shield_points <= 0:
            self.owner.shipHealth -= damage
            return

        self.current_shield_points -= damage

        if self.current_shield_points <= 0:
            leftover = abs(self.current_shield_points)
            self.current_shield_points = 0
            self._is_depleted = True

            # 🔑 APPLY REMAINDER TO HEALTH
            self.owner.shipHealth -= leftover

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

    def reset_recharge_timer(self) -> None:
        self._last_damage_time = pygame.time.get_ticks()

    def reset(self) -> None:
        self.current_shield_points = self.max_shield_points
        self._is_depleted = False
        self._last_damage_time = 0
        self._last_hit_time = -self.courtesy_invincibility_duration
