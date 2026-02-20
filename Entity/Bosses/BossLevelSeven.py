import math
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
        self.attack180_cd_timer = Timer(.4)  # cooldown between swings

        self.attack180_state = 0  # 0=idle, 1=windup, 2=swing
        self.attack180_dir = pygame.Vector2(0, 0)  # locked direction
        self.attack_swipe_counter: int = 0
        self.attack_sequence_one: bool = False
        self.attack_sequence_two: bool = False
        self.attack_sequence_three: bool = False
        self.sequence_one_direction: int = 1 # 1 for right, -1 for left
        self.attack_buffer_timer = Timer(2.0)  # 2 second buffer between attacks

    def barrage_360(self, state) -> None:
        """
        360 barrage with ROF (rate-of-fire) so bullets don't overlap.
        Put this INSIDE BossLevelSeven.
        """

        if self.camera is None:
            return

        # ---------- local ROF gate (no __init__ required) ----------
        rate_of_fire_ms = 350  # fire a burst step every 120ms (tune this)
        now = pygame.time.get_ticks()

        if not hasattr(self, "_barrage360_last_shot_ms"):
            self._barrage360_last_shot_ms = 0

        if now - self._barrage360_last_shot_ms < rate_of_fire_ms:
            return

        self._barrage360_last_shot_ms = now

        # ---------- one "ring step" per ROF tick ----------
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        bullet_speed = 1.8
        bullet_damage = 12
        bullet_color = self.bulletColor

        # keep these SMALL if you want less overlap visually
        bullet_width = 6
        bullet_height = 6

        bullet_count = 4

        # optional: rotate the 8 directions over time so it looks like a spinning spray
        # (prevents repeated overlap on the exact same lines)
        spin_step = 0.0
        if not hasattr(self, "_barrage360_spin"):
            self._barrage360_spin = 0.0
        self._barrage360_spin += 0.10  # radians per tick (tune this)
        spin_step = self._barrage360_spin

        for i in range(bullet_count):
            angle = (i / bullet_count) * (2 * math.pi) + spin_step
            vx = math.cos(angle)
            vy = math.sin(angle)

            b = Bullet(cx, cy)
            b.width = bullet_width
            b.height = bullet_height
            b.color = bullet_color
            b.damage = bullet_damage

            b.vx = vx
            b.vy = vy
            b.bullet_speed = bullet_speed

            b.update_rect()
            state.enemy_bullets.append(b)

    def teleport_attack_swipes(self, state) -> None:
        # one-time flag (keeps dash from repeating during the same windup)
        if not hasattr(self, "attack180_dashed"):
            self.attack180_dashed = False

        # ------------------------------------------------------------
        # STATE 0 -> start windup (locks direction + resets dash flag)
        # ------------------------------------------------------------
        if self.attack180_state == 0:
            if self.attack180_cd_timer.is_ready():
                # lock direction toward player ONCE
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

                self.attack180_dashed = False
                self.attack180_windup_timer.reset()
                self.attack180_state = 1
                return  # freeze during windup

        # ------------------------------------------------------------
        # STATE 1 -> WINDUP (dash once, then wait for windup to finish)
        # ------------------------------------------------------------
        if self.attack180_state == 1:
            # DASH 50px toward player ONCE at the start of windup
            if not self.attack180_dashed and self.target_player is not None:
                ex = self.x + self.width / 2
                ey = self.y + self.height / 2
                px = self.target_player.x + self.target_player.width / 2
                py = self.target_player.y + self.target_player.height / 2

                dx = px - ex
                dy = py - ey
                dist = (dx * dx + dy * dy) ** 0.5

                if dist != 0:
                    dash = 110.0
                    step = min(dash, dist)  # don't overshoot past player
                    self.x += (dx / dist) * step
                    self.y += (dy / dist) * step
                    self.update_hitbox()

                self.attack180_dashed = True

            # when windup finishes -> enter swing
            if self.attack180_windup_timer.is_ready():
                self.attack180_swing_timer.reset()
                self.attack180_state = 2

            return  # still frozen during windup

        # ------------------------------------------------------------
        # STATE 2 -> SWING
        # ------------------------------------------------------------
        if self.attack180_state == 2:
            base = max(self.width, self.height)
            side = int(base * 1.6)  # square

            ex = self.x + self.width / 2
            ey = self.y + self.height / 2

            push = side * 0.35
            cx = ex + self.attack180_dir.x * push
            cy = ey + self.attack180_dir.y * push

            # square centered on (cx, cy)
            self.attack180_rect = pygame.Rect(
                int(cx - side / 2),
                int(cy - side / 2),
                side,
                side
            )

            if self.attack180_rect.colliderect(state.starship.hitbox) and not state.starship.invincible:
                state.starship.shield_system.take_damage(25)
                state.starship.on_hit()

            if self.attack180_swing_timer.is_ready():
                self.attack_swipe_counter += 1
                if self.attack_swipe_counter > 3:
                    self.attack_swipe_counter = 0
                print(self.attack_swipe_counter)
                self.attack180_cd_timer.reset()
                self.attack180_state = 0
                self.attack180_rect = None
                print("ATTACK180 END")

            return

        # not swinging
        self.attack180_rect = None

        if not self.is_active:
            return

        now = pygame.time.get_ticks()
        time_left_ms = 5000 - (now - self.attack_choice_timer.last_time_ms)
        if time_left_ms < 0:
            time_left_ms = 0

        if time_left_ms == 0:
            attack_chooser_roll = random.randint(1, 100)

            if attack_chooser_roll <= 50:
                print("attack 1")  # 50%
            elif attack_chooser_roll <= 80:
                print("attack 2")  # 30% (51-80)
            else:
                print("attack 3")  # 20% (81-100)

            self.attack_choice_timer.last_time_ms = now

    def update(self, state) -> None:
        super().update(state)
        now = pygame.time.get_ticks()
        time_left_ms = 5000 - (now - self.attack_choice_timer.last_time_ms)
        if time_left_ms < 0:
            time_left_ms = 0
        # print(time_left_ms)

        # fire when countdown hits 0, then reset
        if time_left_ms == 0:
            attack_chooser_roll = random.randint(1, 100)

            # Reset sequences
            self.attack_sequence_one = False
            self.attack_sequence_two = False
            self.attack_sequence_three = False

            if attack_chooser_roll <= 50:
                print("attack 1")  # 50%
                self.attack_sequence_one = True
                self.is_firing = True
                self.fire_phase_timer.reset()
            elif attack_chooser_roll <= 80:
                print("attack 2")  # 30% (51-80)
                self.attack_sequence_two = True
            else:
                print("attack 3")  # 20% (81-100)
                self.attack_sequence_three = True

            # Reset the buffer timer so there is a 2-second delay before the next attack begins
            self.attack_buffer_timer.reset()

            # reset start time to "now" so the next 5s countdown begins
            self.attack_choice_timer.last_time_ms = now
        # self.barrage_360(state)
        # put this INSIDE BossLevelSeven.update(), replacing your current dash/windup/swing transition
        # (this is ONLY the "dash 50px before each swipe" flow)

        if self.attack_buffer_timer.is_ready():
            if self.attack_sequence_one:
                if self.is_firing:
                    # FIRE PHASE
                    if self.machine_gun_timer.is_ready():
                        self.shoot_multiple_down_vertical_y(
                            bullet_speed=-4.0,
                            bullet_width=55,
                            bullet_height=10,
                            bullet_color=self.bulletColor,
                            bullet_damage=10,
                            bullet_count=1,
                            bullet_spread=50,
                            state=state
                        )
                        self.machine_gun_timer.reset()

                    # end FIRE phase → switch to REST
                    if self.fire_phase_timer.is_ready():
                        self.is_firing = False
                        self.rest_phase_timer.reset()

            elif self.attack_sequence_two:
                self.teleport_attack_swipes(state)
            elif self.attack_sequence_three:
                # Maybe some other attack here if needed, but for now just move to center
                self.barrage_360(state)

        self.moveAI()

        # WORLD-SPACE hitbox
        self.update_hitbox()
        now = pygame.time.get_ticks()

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

            # END REST → switch to FIRE
            # if self.rest_phase_timer.is_ready():
            #     self.is_firing = True
            #     self.fire_phase_timer.reset()
            #     self.machine_gun_timer.reset()

        now = pygame.time.get_ticks()


        self.last_shot_time = now

    def moveAI(self) -> None:
        if self.camera is None:
            return

        z = self.camera.zoom
        view_w = self.camera.window_width / z
        view_h = self.camera.window_height / z

        if self.attack_sequence_one:
            # Sequence one: enemy goes to bottom of screen and moves left to right
            target_y = self.camera.y + view_h - self.height

            # Move to bottom first
            dy = target_y - self.y
            if abs(dy) > 0.5:
                step_y = min(self.moveSpeed, abs(dy))
                self.y += step_y if dy > 0 else -step_y

            # Move left to right (ping pong)
            self.x += self.moveSpeed * self.sequence_one_direction

            # Bounce off edges
            if self.x <= 0:
                self.x = 0
                self.sequence_one_direction = 1
            elif self.x >= view_w - self.width:
                self.x = view_w - self.width
                self.sequence_one_direction = -1

        elif self.attack_sequence_two:
            # Sequence two: print("movement handled in attack")
            print("movement handled in attack")

        elif self.attack_sequence_three:
            # Sequence three: move enemy to center of screen
            target_x = (view_w / 2) - (self.width / 2)
            target_y = self.camera.y + (view_h / 2) - (self.height / 2)

            dx = target_x - self.x
            dy = target_y - self.y

            if abs(dx) > 0.5:
                step_x = min(self.moveSpeed, abs(dx))
                self.x += step_x if dx > 0 else -step_x

            if abs(dy) > 0.5:
                step_y = min(self.moveSpeed, abs(dy))
                self.y += step_y if dy > 0 else -step_y

        else:
            # Default behavior (from existing moveAI)
            # CENTER of the current camera view (WORLD)
            target_x = (view_w / 2) - (self.width / 2)
            target_y = self.camera.y + (view_h / 2) - (self.height / 2)

            dx = target_x - self.x
            dy = target_y - self.y

            if abs(dx) > 0:
                step_x = min(self.moveSpeed, abs(dx))
                self.x += step_x if dx > 0 else -step_x

            if abs(dy) > 0:
                step_y = min(self.moveSpeed, abs(dy))
                self.y += step_y if dy > 0 else -step_y

            self.y -= 1  # requested drift upward

        # Clamp to visible camera window
        left = 0.0
        right = view_w - self.width
        top = self.camera.y
        bottom = self.camera.y + view_h - self.height

        if self.x < left:
            self.x = left
        elif self.x > right:
            self.x = right

        if self.y < top:
            self.y = top
        elif self.y > bottom:
            self.y = bottom


    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)
        if not getattr(self, "is_active", True):
            return

            # if this bullet is a beam bullet, draw as a beam and exit
        if hasattr(self, "beam_length"):
            self.draw_laser_beam(surface, camera)
            return

            # otherwise draw normal bullet (your existing logic)
        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)
        pygame.draw.rect(
            surface,
            self.color,
            pygame.Rect(
                int(screen_x),
                int(screen_y),
                int(self.width * camera.zoom),
                int(self.height * camera.zoom),
            ),
        )

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

    # Put this INSIDE Bullet (or wherever your Bullet.draw lives).
    # This is NOT Bullet.draw. This is the helper you call FROM Bullet.draw.

    def draw_laser_beam(self, surface: pygame.Surface, camera) -> None:
        """
        Draw a SINGLE rectangle "beam" (not a ring).
        Uses fields set by barrage_360:
          self.beam_origin_x, self.beam_origin_y, self.beam_length, self.beam_thick, self.beam_angle
          plus self.vx/self.vy (unit direction) and self.color
        """
        if not hasattr(self, "beam_length"):
            return

        z = camera.zoom

        # START point (SCREEN)
        sx = camera.world_to_screen_x(self.beam_origin_x)
        sy = camera.world_to_screen_y(self.beam_origin_y)

        # LENGTH + THICKNESS (SCREEN)
        beam_len_px = max(1, int(self.beam_length * z))
        beam_thick_px = max(1, int(self.beam_thick * z))

        # single rect surface, then rotate it
        beam_surf = pygame.Surface((beam_len_px, beam_thick_px), pygame.SRCALPHA)
        beam_surf.fill(self.color)

        angle_deg = math.degrees(self.beam_angle)
        rotated = pygame.transform.rotate(beam_surf, angle_deg)

        # place so it STARTS at (sx, sy) and extends outward
        mid_x = sx + (self.vx * (beam_len_px / 2))
        mid_y = sy + (self.vy * (beam_len_px / 2))
        r = rotated.get_rect(center=(mid_x, mid_y))

        surface.blit(rotated, r)
