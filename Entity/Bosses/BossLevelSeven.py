import random
import pygame
from pygame import surface

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Entity.Monsters.RescuePod import RescuePod
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelSeven(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.name: str = "BossLevelSeven"
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20
        self.fire_interval_ms: int = 2000
        self.last_shot_time: int = 0
        self.speed: float = 0.4
        self.enemyHealth: float = 3000.0
        self.maxHealth: float = 3000.0
        self.exp: int = 1
        self.credits: int = 5
        # No longer using self.enemyBullets - using game_state.enemy_bullets instead
        self.moveSpeed: float = 2.2
        self.edge_padding: int = 0
        self.move_direction: int = random.choice([-1, 1])
        self.move_interval_ms: int = 3000
        self.last_move_toggle: int = pygame.time.get_ticks()
        self.is_moving: bool = True
        # __init__

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image
        self.touch_damage: int = 10
        # state machine
        self.is_firing = False

        self.fire_phase_timer = Timer(5.0)  # how long FIRE lasts
        self.rest_phase_timer = Timer(10.0)  # how long REST lasts
        self.machine_gun_timer = Timer(0.5)  # fire rate during FIRE
        self.aimed_shot_timer = Timer(1.0)  # 1 second

        # __init__ (add this with your other timers)
        self.attack_choice_timer = Timer(5000)  # 5 seconds

        # --- BossLevelSeven.__init__ (timers + 2 small state vars) ---
        self.attack180_windup_timer = Timer(0.5)  # stop before swing
        self.attack180_swing_timer = Timer(0.2)  # swing active window
        self.attack180_cd_timer = Timer(1.0)  # cooldown between swings

        self.attack180_state = 0  # 0=idle, 1=windup, 2=swing
        self.attack180_dir = pygame.Vector2(0, 0)  # locked direction

    def update(self, state) -> None:
        super().update(state)
        # --- BossLevelSeven.update (drop this near the top, BEFORE moveAI) ---
        # NOTE: windup/swing stops movement by returning early.

        # start attack if idle + cooldown ready
        if self.attack180_state == 0:
            if self.attack180_cd_timer.is_ready():
                # lock direction ONCE (berserker swing)
                ex = self.x + self.width / 2
                ey = self.y + self.height / 2
                px = state.starship.hitbox.centerx
                py = state.starship.hitbox.centery

                dx = px - ex
                dy = py - ey
                dist = (dx * dx + dy * dy) ** 0.5
                if dist != 0:
                    self.attack180_dir.x = dx / dist
                    self.attack180_dir.y = dy / dist

                self.attack180_windup_timer.reset()
                self.attack180_state = 1
                print("ATTACK180 WINDUP")
                return  # stop movement during windup

        # windup (0.5s frozen)
        if self.attack180_state == 1:
            if self.attack180_windup_timer.is_ready():
                self.attack180_swing_timer.reset()
                self.attack180_state = 2
                print("ATTACK180 SWING")
            return  # still frozen until swing starts

        # swing active (0.2s)
        # swing active (0.2s)
        # ----------------------------
        # UPDATE: build the swing box
        # ----------------------------
        # ATTACK180 SWING (ACTIVE)
        # ----------------------------
        if self.attack180_state == 2:
            base = max(self.width , self.height )
            side = int(base * 1.6)  # square, 40% bigger than enemy

            ex = self.x + self.width / 2
            ey = self.y + self.height / 2

            push = side * 0.35
            cx = ex + self.attack180_dir.x * push
            cy = ey + self.attack180_dir.y * push

            # square centered on (cx, cy)
            self.attack180_rect = pygame.Rect(
                int(cx - side / 2 ),
                int(cy - side / 2 ),
                side,
                side
            )

            # collision uses the same rect you just built
            if self.attack180_rect.colliderect(state.starship.hitbox) and not state.starship.invincible:
                state.starship.shield_system.take_damage(25)
                state.starship.on_hit()

            # end swing
            if self.attack180_swing_timer.is_ready():
                self.attack180_cd_timer.reset()
                self.attack180_state = 0
                self.attack180_rect = None
                print("ATTACK180 END")

            return

        # not swinging
        self.attack180_rect = None

        if not self.is_active:
            return
        # countdown (ms remaining until ready)
        now = pygame.time.get_ticks()
        time_left_ms = 5000 - (now - self.attack_choice_timer.last_time_ms)
        if time_left_ms < 0:
            time_left_ms = 0
        # print(time_left_ms)

        # fire when countdown hits 0, then reset
        if time_left_ms == 0:
            attack_chooser_roll = random.randint(1, 100)

            if attack_chooser_roll <= 50:
                print("attack 1")  # 50%
            elif attack_chooser_roll <= 80:
                print("attack 2")  # 30% (51-80)
            else:
                print("attack 3")  # 20% (81-100)

            # reset start time to "now" so the next 5s countdown begins
            self.attack_choice_timer.last_time_ms = now

        # self.moveAI()

        # WORLD-SPACE hitbox
        self.update_hitbox()

        # Always update the blade position in every frame
            # update

        # -------------------------
        # FIRE / REST STATE MACHINE
        # -------------------------

        # if self.is_firing:
        #     # FIRE PHASE
        #     if self.machine_gun_timer.is_ready():
        #         self.shoot_multiple_down_vertical_y(
        #             bullet_speed=-4.0,
        #             bullet_width=55,
        #             bullet_height=10,
        #             bullet_color=self.bulletColor,
        #             bullet_damage=10,
        #             bullet_count=1,
        #             bullet_spread=50,
        #             state=state
        #         )
        #         self.machine_gun_timer.reset()
        #
        #     # end FIRE phase → switch to REST
        #     if self.fire_phase_timer.is_ready():
        #
        #         self.is_firing = False
        #         self.rest_phase_timer.reset()
        #
        # else:
        #     # REST PHASE — aimed shot every 1 second
        #     if self.aimed_shot_timer.is_ready():
        #         self.shoot_single_bullet_aimed_at_player(
        #             bullet_speed=4.0,
        #             bullet_width=20,
        #             bullet_height=20,
        #             bullet_color=self.bulletColor,
        #             bullet_damage=10,
        #             state=state
        #         )
        #         self.aimed_shot_timer.reset()
        #
        #     # END REST → switch to FIRE
        #     if self.rest_phase_timer.is_ready():
        #         self.is_firing = True
        #         self.fire_phase_timer.reset()
        #         self.machine_gun_timer.reset()

        now = pygame.time.get_ticks()


        self.last_shot_time = now
    def moveAI(self) -> None:
        window_width = GlobalConstants.BASE_WINDOW_WIDTH

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
            if self.move_direction > 0:
                self.mover.enemy_move_right(self)
            else:
                self.mover.enemy_move_left(self)



        self._last_x = self.x

    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)

        if not self.is_active:
            return

        # SPRITE
        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.bile_spitter_image.subsurface(sprite_rect)

        z = camera.zoom
        sprite = pygame.transform.scale(
            sprite,
            (int(self.width * z), int(self.height * z))
        )

        surface.blit(
            sprite,
            (camera.world_to_screen_x(self.x), camera.world_to_screen_y(self.y))
        )

        # ATTACK180 DEBUG DRAW (SQUARE)
        if getattr(self, "attack180_state", 0) == 2 and getattr(self, "attack180_rect", None) is not None:
            r = self.attack180_rect
            pygame.draw.rect(
                surface,
                (255, 0, 0),
                pygame.Rect(
                    int(camera.world_to_screen_x(r.x)),
                    int(camera.world_to_screen_y(r.y)),
                    int(r.width * z),
                    int(r.height * z),
                ),
                2
            )
