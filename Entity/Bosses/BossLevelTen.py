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
        self.enemyHealth: float = 444.0
        self.maxHealth: float = 444.0
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
        self.dragons_breath_timer = Timer(13.0)
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
        # print(f"BOSS HP%: {hp_pct:.1f}, Phase1={self.phase_1}, Phase2={self.phase_2}, Phase3={self.phase_3}, resting={self.is_resting}")

        # Phase transition resets
        new_phase_1 = False
        new_phase_2 = False
        new_phase_3 = False
        # print("P3", "resting=", self.is_resting, "breath_ready=", self.dragons_breath_timer.is_ready(), "active=",
        #       self._dragon_breath_active)
        #
        # if hp_pct > 70:
        #     new_phase_1 = True
        # elif hp_pct > 40:
        #     new_phase_2 = True
        # else:
        #     new_phase_3 = True

        if hp_pct > 80:
            new_phase_1 = True
        elif hp_pct > 60:
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
                    self._dragon_breath_start_time = now
                    self._dragon_breath_end_time = now + 10000  # 10 seconds
                    self.dragons_breath_timer.reset()

                # RUN breath every frame until duration ends
                if self._dragon_breath_active:
                    if now >= self._dragon_breath_end_time:
                        self._dragon_breath_active = False
                        # Delay other attacks by 7 seconds from NOW
                        self.liquid_launcher_timer.delay(7000)
                        self.boomerang_timer.delay(7000)
                        # Chance to rest after attack
                        if random.random() < 0.3:
                            self.is_resting = True
                            self.rest_start_time = pygame.time.get_ticks()
                    else:
                        self.dragons_breath(
                            monster_x=self.x,
                            monster_y=self.y,
                            monster_width=self.width,
                            monster_height=self.height,
                            length=350,
                            min_width=10,
                            max_width=60,
                            segments=12,
                            color=(255, 120, 0),
                            damage=18,
                            x_offset=0,
                            y_offset=0,
                            state=state
                        )
                    return # Exit early so NO other attacks can be evaluated in this frame
                elif self.liquid_launcher_timer.is_ready():
                    self.liquid_launcher_timer.reset()
                    self.dragons_breath_timer.delay(5000)
                    self.boomerang_timer.delay(2000)

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
                    # Chance to rest after attack
                    if random.random() < 0.3:
                        self.is_resting = True
                        self.rest_start_time = pygame.time.get_ticks()

                elif self.boomerang_timer.is_ready():
                    self.boomerang_timer.reset()
                    self.dragons_breath_timer.delay(5000)
                    self.liquid_launcher_timer.delay(2000)

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

    def dragons_breath(
            self,
            monster_x: float,
            monster_y: float,
            monster_width: int,
            monster_height: int,
            length: int,
            min_width: int,
            max_width: int,
            segments: int,
            color: tuple[int, int, int],
            damage: int,
            x_offset: int,
            y_offset: int,
            state
    ) -> None:
        """Original dragons_breath method moved from Enemy class directly into BossLevelTen.
        Caller should manage the duration and active state.
        """
        if state is None:
            return

        # spawn cadence (Timer is in SECONDS in your project)
        if not hasattr(self, "_dragon_breath_timer"):
            self._dragon_breath_timer = Timer(0.05)  # 50ms
            self._dragon_breath_timer.reset()

        # spawn flame particles repeatedly while active
        if not self._dragon_breath_timer.is_ready():
            return

        self._dragon_breath_timer.reset()

        num_bullets = segments if segments > 0 else 1

        base_x = monster_x + monster_width // 2 + x_offset
        base_y = monster_y + monster_height // 2 + y_offset

        print(f"DRAGONS BREATH FIRE: pos=({base_x:.1f}, {base_y:.1f}), target_player={self.target_player is not None}")

        # aim at player if available, else downward
        target_angle = 90.0
        if getattr(self, "target_player", None) is not None:
            dx = (self.target_player.x + self.target_player.width // 2) - base_x
            dy = (self.target_player.y + self.target_player.height // 2) - base_y
            target_angle = math.degrees(math.atan2(dy, dx))

        spread_angle = math.degrees(math.atan2(max_width / 2, length)) * 2

        for _ in range(num_bullets):
            angle_offset = random.uniform(-spread_angle / 2, spread_angle / 2)
            angle_rad = math.radians(target_angle + angle_offset)

            b = Bullet(base_x, base_y)
            b.vx = math.cos(angle_rad)
            b.vy = math.sin(angle_rad)

            b.bullet_speed = random.uniform(4.0, 6.0)
            b.color = color
            b.damage = damage
            b.width = min_width
            b.height = min_width

            b.start_x = float(base_x)
            b.start_y = float(base_y)
            b.max_range = float(length)

            # 🔥 CRITICAL: VerticalBattleScreen uses world_to_screen based on x,y
            # We must make sure the bullet starts visible
            b.camera = getattr(self, "camera", None)

            def flame_update(bullet=b, start_w=min_width, end_w=max_width, max_r=float(length)):
                # 🛠️ SETUP: track true center for movement math
                if not hasattr(bullet, "true_x"):
                    bullet.true_x = bullet.x
                    bullet.true_y = bullet.y

                # 🚀 MOVE: manual movement using true center
                bullet.true_x += bullet.vx * bullet.bullet_speed
                bullet.true_y += bullet.vy * bullet.bullet_speed

                # 📏 DISTANCE: check range based on true center
                dx2 = bullet.true_x - bullet.start_x
                dy2 = bullet.true_y - bullet.start_y
                dist_sq = dx2 * dx2 + dy2 * dy2
                max_sq = max_r * max_r

                if dist_sq >= max_sq:
                    bullet.is_active = False
                    return

                # 🌊 SCALE: increase size over distance
                dist = math.sqrt(dist_sq)
                t = dist / max_r
                current_size = start_w + (end_w - start_w) * t
                bullet.width = int(current_size)
                bullet.height = int(current_size)

                # 🎯 HITBOX: update centered on true_x/y
                bullet.rect.x = int(bullet.true_x - bullet.width // 2)
                bullet.rect.y = int(bullet.true_y - bullet.height // 2)
                bullet.rect.width = bullet.width
                bullet.rect.height = bullet.height

                # 🎨 DRAW: set bullet.x/y to rect.x/y for VerticalBattleScreen.draw (top-left)
                bullet.x = float(bullet.rect.x)
                bullet.y = float(bullet.rect.y)

                # 📽️ CAMERA: manual deactivation with extra buffer
                if bullet.camera:
                    # In world coordinates, screen area is (camera.y) to (camera.y + window_height/zoom)
                    visible_top = bullet.camera.y - 500
                    visible_bottom = (
                            bullet.camera.y
                            + (bullet.camera.window_height / bullet.camera.zoom)
                            + 500
                    )
                    # Use center (true_y) for deactivation check
                    if bullet.true_y < visible_top or bullet.true_y > visible_bottom:
                        bullet.is_active = False

            b.update = flame_update
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
            state=state
        )

