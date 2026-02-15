import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle


class SpinalRaptor(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement
        self.mover: MoveRectangle = MoveRectangle()
        self.move_direction: int = random.choice([-1, 1])
        self.moveSpeed: float = 2.2
        self.edge_padding: int = 0

        # identity / visuals
        self.name: str = "SpinalRaptor"
        self.width: int = 40
        self.height: int = 40
        self.color = GlobalConstants.RED

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image

        # stats
        self.enemyHealth: float = 25.0
        self.maxHealth: float = 25.0
        self.exp: int = 1
        self.credits: int = 5

        # ranged attack
        self.bulletColor = GlobalConstants.SKYBLUE
        self.attack_timer = Timer(3.0)

        # touch damage
        self.touch_damage: int = 10
        self.touch_timer = Timer(0.75)

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return


        self.update_hitbox()

        if state.starship.current_level != 3:
            if self.is_active and self.attack_timer.is_ready():
                self.shoot_single_bullet_aimed_at_player(
                    bullet_speed=3.5,
                    bullet_width=20,
                    bullet_height=20,
                    bullet_color=self.bulletColor,
                    bullet_damage=40,
                    state=state
                )
                self.attack_timer.reset()

        else:
            if self.is_active and self.attack_timer.is_ready():
                self.shoot_single_bullet_aimed_at_player(
                    bullet_speed=2.5,
                    bullet_width=20,
                    bullet_height=20,
                    bullet_color=self.bulletColor,
                    bullet_damage=40,
                    state=state
                )
                self.attack_timer.reset()

        # 🔑 CALL TOUCH DAMAGE HANDLER
        self.player_collide_damage(state.starship)
        self.moveAI(state)
        self.pounce()


    # -------------------------------------------------
    # TOUCH DAMAGE (STANDALONE FUNCTION)
    # -------------------------------------------------

    # -------------------------------------------------
    # MOVEMENT
    # -------------------------------------------------
    def moveAI(self, state) -> None:
        window_width = GlobalConstants.BASE_WINDOW_WIDTH

        # 1) IF RESCUE POD AND PLAYER ON SCREEN -> HUNT NPC
        from Entity.Monsters.RescuePod import RescuePod

        # Check if player is on screen
        player_on_screen = self.mover.enemy_on_screen(state.starship, self.camera)

        if player_on_screen:
            # Look for a RescuePod that is also on screen
            target_pod = None

            # Check state.enemies
            for enemy in state.enemies:
                if isinstance(enemy, RescuePod):
                    if self.mover.enemy_on_screen(enemy, self.camera):
                        target_pod = enemy
                        break

            # Also check self.rescue_pod_group if it exists (some levels keep them separate)
            if not target_pod and hasattr(self, "rescue_pod_group") and self.rescue_pod_group:
                for pod in self.rescue_pod_group:
                    if self.mover.enemy_on_screen(pod, self.camera):
                        target_pod = pod
                        break

            if target_pod:
                self.Hunt_NPC(target_pod, state)
                return

        # 2) DEFAULT MOVEMENT (Horizontal Pacing)
        if not hasattr(self, "_last_x"):
            self._last_x = self.x

        if self.move_direction > 0:
            self.mover.enemy_move_right(self)
        else:
            self.mover.enemy_move_left(self)

        if self.x < self.edge_padding:
            self.x = self.edge_padding
        elif self.x + self.width > window_width - self.edge_padding:
            self.x = window_width - self.edge_padding - self.width

        if self.x == self._last_x:
            self.move_direction *= -1

        self._last_x = self.x

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------
    def draw(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        super().draw(surface, camera)

        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.bile_spitter_image.subsurface(sprite_rect)

        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        surface.blit(
            scaled_sprite,
            (
                camera.world_to_screen_x(self.x),
                camera.world_to_screen_y(self.y),
            )
        )


