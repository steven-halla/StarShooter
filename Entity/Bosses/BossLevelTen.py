import random
import pygame
from pygame import surface

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Entity.Monsters.RescuePod import RescuePod
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelTen(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.name: str = "BossLevelTen"
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 10
        self.bulletHeight: int = 10
        self.fire_interval_ms: int = 2000
        self.last_shot_time: int = 0
        self.speed: float = 0.4
        self.enemyHealth: float = 1111.0
        self.maxHealth: float = 1111.0
        self.exp: int = 1
        self.credits: int = 5
        # No longer using self.enemyBullets - using game_state.enemy_bullets instead
        self.moveSpeed: float = 0.9
        self.edge_padding: int = 0
        self.move_direction: int = random.choice([-1, 1])
        self.move_interval_ms: int = 3000
        self.last_move_toggle: int = pygame.time.get_ticks()
        self.is_moving: bool = True
        # __init__
        self.attack_timer = Timer(3.0)  # 3 seconds

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.bile_spitter_image
        self.touch_damage: int = 10
        # state machine
        self.is_firing = False


        self.phase_1 = True
        self.phase_2 = False
        self.phase_3 = False
        self.target_player = None

        self.liquid_launcher_timer = Timer(6.0)
        self.boomerang_timer = Timer(9.0)
        self.dragons_breath_timer = Timer(4.0)
        self.horizontal_barrage_timer = Timer(8.0)

        self.is_resting = False
        self.rest_start_time = 0
        self._rope = None
        self.player_caught: bool = False
        self._dragon_breath_active = False
        self._dragon_breath_end_time = 0

    def update(self, state) -> None:
        super().update(state)
        # print(self.phase_2)
        if not self.is_active:
            return

        now = pygame.time.get_ticks()
        self.target_player = state.starship

        hp_pct = (self.enemyHealth / self.maxHealth) * 100 if self.maxHealth else 0

        # Phase transition resets
        # new_phase_1 = False
        # new_phase_2 = False
        # new_phase_3 = True

        if hp_pct > 70:
            new_phase_1 = True
        elif hp_pct > 40:
            new_phase_2 = True
        else:
            new_phase_3 = True

        # If transitioning INTO Phase 2, reset its timers so they don't fire immediately
        # based on old timestamps from Phase 1
        if new_phase_2 and not self.phase_2:
            self.boomerang_timer.reset()
            self.horizontal_barrage_timer.reset()

        if new_phase_3 and not self.phase_3:
            self.dragons_breath_timer.reset()
            self.liquid_launcher_timer.reset()
            self.boomerang_timer.reset()

        self.phase_1 = new_phase_1
        self.phase_2 = new_phase_2
        self.phase_3 = new_phase_3

        if self.phase_1:
            if self.liquid_launcher_timer.is_ready():
                self.liquid_launcher_timer.reset()
                self.liquid_launcher(
                    damage=20,
                    air_height=180.0,
                    bullet_spread=40,
                    bullet_number=5,
                    width=14,
                    height=14,
                    color=self.bulletColor,
                    bullet_speed=4.0,
                    state=state
                )

        elif self.phase_2:
            if not self.is_resting:
                if self.boomerang_timer.is_ready():
                    self.boomerang_timer.reset()
                    self.boomerang(
                        power=15,
                        bullet_number=4,
                        width=20,
                        height=20,
                        color=GlobalConstants.RED,
                        speed=4.0,
                        max_distance_traveled=300.0,
                        bullet_spread=15.0,
                        state=state
                    )
                    # Chance to rest after attack
                    if random.random() < 0.3:
                        self.is_resting = True
                        self.rest_start_time = pygame.time.get_ticks()

                elif self.horizontal_barrage_timer.is_ready():
                    self.horizontal_barrage_timer.reset()
                    self.horizontal_barrage(state)
                    # Chance to rest after attack
                    if random.random() < 0.3:
                        self.is_resting = True
                        self.rest_start_time = pygame.time.get_ticks()

        elif self.phase_3:
            if not self.is_resting:
                now = pygame.time.get_ticks()
                # active window tracking (init each field independently)
                if not hasattr(self, "_dragon_breath_active"):
                    self._dragon_breath_active = False

                if not hasattr(self, "_dragon_breath_start_time"):
                    self._dragon_breath_start_time = 0

                # START breath
                if self.dragons_breath_timer.is_ready() and not self._dragon_breath_active:
                    self._dragon_breath_active = True
                    self._dragon_breath_end_time = now + 10000  # 10 seconds
                    self.dragons_breath_timer.reset()

                # RUN breath every frame until duration ends
                if self._dragon_breath_active:
                    if now >= self._dragon_breath_end_time:
                        self._dragon_breath_active = False
                    else:
                        self.dragons_breath(
                            monster_x=self.x,
                            monster_y=self.y,
                            monster_width=self.width,
                            monster_height=self.height,
                            length=120,
                            min_width=10,
                            max_width=60,
                            segments=6,
                            color=(255, 120, 0),
                            damage=18,
                            x_offset=0,
                            y_offset=0,
                            state=state,
                            duration_ms=10000
                        )
                elif self.liquid_launcher_timer.is_ready():
                    self.liquid_launcher_timer.reset()
                    self.dragons_breath_timer.last_time_ms += 1000
                    self.boomerang_timer.last_time_ms += 2000

                    self.liquid_launcher(
                        damage=20,
                        air_height=180.0,
                        bullet_spread=40,
                        bullet_number=5,
                        width=14,
                        height=14,
                        color=self.bulletColor,
                        bullet_speed=4.0,
                        state=state
                    )

                elif self.boomerang_timer.is_ready():
                    self.boomerang_timer.reset()
                    self.dragons_breath_timer.last_time_ms += 1000
                    self.liquid_launcher_timer.last_time_ms += 2000

                    self.boomerang(
                        power=15,
                        bullet_number=4,
                        width=20,
                        height=20,
                        color=GlobalConstants.RED,
                        speed=4.0,
                        max_distance_traveled=300.0,
                        bullet_spread=15.0,
                        state=state
                    )

        self.moveAI(state)

        # WORLD-SPACE hitbox
        self.update_hitbox()

        now = pygame.time.get_ticks()

    def moveAI(self, state) -> None:

        if self.phase_1:
            # use the SAME world-width that Enemy.clamp_horizontal() uses
            if self.camera is None:
                return
            max_x = (self.camera.window_width / self.camera.zoom) - self.width

            if not hasattr(self, "_phase1_dir"):
                self._phase1_dir = random.choice([-1, 1])

            # move left/right
            if self._phase1_dir > 0:
                self.mover.enemy_move_right(self)
            else:
                self.mover.enemy_move_left(self)

            # clamp + bounce (>= / <= so it can't "stick" on the edge)
            if self.x <= 0:
                self.x = 0
                self._phase1_dir = 1
            elif self.x >= max_x:
                self.x = max_x
                self._phase1_dir = -1

        elif self.phase_2 or self.phase_3:
            now = pygame.time.get_ticks()

            # REST: only blocks ATTACKS elsewhere, NOT movement
            if self.is_resting and (now - self.rest_start_time >= 5000):
                self.is_resting = False

            # ALWAYS chase the player (no early returns)
            if state.starship:
                dx = state.starship.x - self.x
                dy = state.starship.y - self.y
                self.mover.enemy_move(self, dx, dy)

        elif self.phase_3:
            self.moveSpeed = 0.7

    def draw(self, surface: pygame.Surface, camera):
        # self.draw_bomb(surface, self.camera)

        super().draw(surface, camera)

        if not self.is_active:
            return
        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.bile_spitter_image.subsurface(sprite_rect)

        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)
        surface.blit(scaled_sprite, (screen_x, screen_y))

    def horizontal_barrage(self, state) -> None:
        """Fires 10 bullets from the RIGHT edge of the screen to the LEFT."""
        if self.camera is None:
            return

        # RIGHT of screen in world space
        right_x = self.camera.window_width / self.camera.zoom
        # LEFT of screen in world space is 0 (as horizontal camera doesn't scroll)

        # Screen height in world space
        screen_height_world = self.camera.window_height / self.camera.zoom
        # Top of current screen in world space
        top_y = self.camera.y

        # Calculate Y spacing to spread 10 bullets
        spacing = 40

        for i in range(1, 11):
            bullet_y = top_y + (i * spacing)
            b = Bullet(right_x, bullet_y)
            b.vx = -1.0 # Right to Left
            b.vy = 0.0
            b.bullet_speed = 3.0 # Typical bullet speed
            b.width = self.bulletWidth
            b.height = self.bulletHeight
            b.damage = 10
            b.camera = self.camera

            # Using game_state.enemy_bullets as per comment on line 32
            state.enemy_bullets.append(b)

    def flame_thrower(self, state) -> None:
        """Calls the dragons_breath attack."""
        self.dragons_breath(
            monster_x=self.x,
            monster_y=self.y,
            monster_width=self.width,
            monster_height=self.height,
            length=200,
            min_width=10,
            max_width=40,
            segments=3,
            color=GlobalConstants.ORANGE,
            damage=15,
            x_offset=0,
            y_offset=0,
            state=state,
            duration_ms=10000
        )

    ###### DO NOT REMOVE The below YOU MOTHER FUCKER these are
        ###### important instructions for this task

#phase 1
# rain - balls shoot up and then down on player, moves enemy left/right
#phase 2
# boomerrange - fires two bullets that travel to player and then back to enemy
#figure 8 attack meellee attack at player
#phase 3 go to center of screen and aim at player
# flame thrower - go center of screen and aim flame thrower at player
#missiles - shoots missiles that target player
