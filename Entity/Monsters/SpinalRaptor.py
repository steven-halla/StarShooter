import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Entity.Monsters.RescuePod import RescuePod


class SpinalRaptor(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # movement
        self.mover: MoveRectangle = MoveRectangle()
        self.move_direction: int = random.choice([-1, 1])
        self.moveSpeed: float = 1.2
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
        self.enemyHealth: float = 20.0
        self.maxHealth: float = 20.0
        self.exp: int = 1
        self.credits: int = 5

        # ranged attack
        self.bulletColor = GlobalConstants.SKYBLUE
        self.attack_timer = Timer(5.0)

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

        # Reset attack timer if player is close (pounce distance)
        dx = state.starship.x - self.x
        dy = state.starship.y - self.y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist <= 80:
            self.attack_timer.reset()

        self.moveAI(state)
        # self.pounce() # moveAI now handles movement


    # -------------------------------------------------
    # TOUCH DAMAGE (STANDALONE FUNCTION)
    # -------------------------------------------------

    # -------------------------------------------------
    # MOVEMENT
    # -------------------------------------------------
    def moveAI(self, state) -> None:
        # 1) Look for a RescuePod that is on screen
        target_pod = None

        # Check state.enemies
        for enemy in state.enemies:
            if isinstance(enemy, RescuePod):
                if self.mover.enemy_on_screen(enemy, self.camera):
                    target_pod = enemy
                    break

        # Also check self.rescue_pod_group if it exists
        if not target_pod and hasattr(self, "rescue_pod_group") and self.rescue_pod_group:
            for pod in self.rescue_pod_group:
                if self.mover.enemy_on_screen(pod, self.camera):
                    target_pod = pod
                    break

        if target_pod:
            self.Hunt_NPC(target_pod, state)
        else:
            # 2) If no pod, move towards player
            dx = state.starship.x - self.x
            dy = state.starship.y - self.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > 0:
                # Check for pounce speed boost
                now = pygame.time.get_ticks()
                if not hasattr(self, "_pounce_active"):
                    self._pounce_active = False
                    self._pounce_start_time = 0
                    self._pounce_cooldown_until = 0

                # ENTER POUNCE
                if (
                    not self._pounce_active
                    and dist <= 80
                    and now >= self._pounce_cooldown_until
                ):
                    self._pounce_active = True
                    self._pounce_start_time = now

                # EXIT POUNCE AFTER 1s
                if self._pounce_active and now - self._pounce_start_time >= 1000:
                    self._pounce_active = False
                    self._pounce_cooldown_until = now + 5000  # 5s cooldown

                speed = self.moveSpeed
                if self._pounce_active:
                    speed = self.moveSpeed * 2.5

                self.x += (dx / dist) * speed
                self.y += (dy / dist) * speed
                self.update_hitbox()

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


