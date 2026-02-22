import random
import pygame
from pygame import surface

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.RescuePod import RescuePod
from Entity.Monsters.Slaver import Slaver
from Entity.Monsters.TriSpitter import TriSpitter
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelNine(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.name: str = "BossLevelNine"
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20
        self.fire_interval_ms: int = 2000
        self.last_shot_time: int = 0
        self.speed: float = 0.4
        self.enemyHealth: float = 1111.0
        self.maxHealth: float = 1111.0
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
        self.attack_timer = Timer(3.0)  # 3 seconds

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

        self.summon_swarm_timer = Timer(20.0)
        self.summon_swarm_timer.reset()

        self.boss_alone: bool = False

    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return
        self.moveAI(state)

        # WORLD-SPACE hitbox
        self.update_hitbox()

        # Always update the blade position in every frame
            # update

        # -------------------------
        # FIRE / REST STATE MACHINE
        # -------------------------

        if self.is_firing:
            # FIRE PHASE
            if self.machine_gun_timer.is_ready():
                self.shoot_multiple_down_vertical_y(
                    bullet_speed=4.0,
                    bullet_width=3,
                    bullet_height=10,
                    bullet_color=self.bulletColor,
                    bullet_damage=10,
                    bullet_count=3,
                    bullet_spread=50,
                    state=state
                )
                self.machine_gun_timer.reset()

            # end FIRE phase → switch to REST
            if self.fire_phase_timer.is_ready():

                self.is_firing = False
                self.rest_phase_timer.reset()

        else:
            # REST PHASE — aimed shot every 1 second
            if self.aimed_shot_timer.is_ready():
                self.shoot_single_bullet_aimed_at_player(
                    bullet_speed=4.0,
                    bullet_width=20,
                    bullet_height=20,
                    bullet_color=self.bulletColor,
                    bullet_damage=10,
                    state=state
                )
                self.aimed_shot_timer.reset()

            # END REST → switch to FIRE
            if self.rest_phase_timer.is_ready():
                self.is_firing = True
                self.fire_phase_timer.reset()
                self.machine_gun_timer.reset()

        now = pygame.time.get_ticks()


        self.last_shot_time = now

        if self.summon_swarm_timer.is_ready():
            self.summon_swarm(state)
            self.summon_swarm_timer.reset()

    def summon_swarm(self, state):
        # Summon one of each: BileSpitter, TriSpitter, BladeSpinner, Slaver
        swarm_classes = [BileSpitter, TriSpitter, BladeSpinner, Slaver]

        # Use camera to ensure they are on screen with player and boss
        camera = getattr(self, "camera", None)
        if not camera:
            # Fallback if camera is not set on boss (though it should be)
            return

        # Visible world area
        view_x = camera.x
        view_y = camera.y
        # The window dimensions are in pixels, we want world dimensions
        # Screen size = World size * zoom => World size = Screen size / zoom
        world_view_w = camera.window_width / camera.zoom
        world_view_h = camera.window_height / camera.zoom

        for enemy_class in swarm_classes:
            enemy = enemy_class()

            # Placement: Randomly on screen, but with some padding
            padding = 40

            # Ensure we don't pick a range where min > max
            range_x = int(world_view_w - 2 * padding - enemy.width)
            range_y = int(world_view_h - 2 * padding - enemy.height)

            offset_x = random.randint(0, max(0, range_x))
            offset_y = random.randint(0, max(0, range_y))

            enemy.x = view_x + padding + offset_x
            enemy.y = view_y + padding + offset_y

            enemy.camera = camera
            enemy.target_player = state.starship
            if hasattr(enemy, "maxHealth"):
                enemy.enemyHealth = enemy.maxHealth
            else:
                enemy.enemyHealth = 1
            enemy.update_hitbox()
            enemy.is_active = True

            state.enemies.append(enemy)

    def moveAI(self, state) -> None:
        now = pygame.time.get_ticks()

        if not hasattr(self, "_debug_last_print"):
            self._debug_last_print = 0

        player = getattr(state, "starship", None)

        enemies = list(getattr(state, "enemies", []))
        active_enemies = [e for e in enemies if getattr(e, "is_active", True)]

        only_boss_and_player = (len(active_enemies) == 1 and active_enemies[0] is self and player is not None)

        if now - self._debug_last_print >= 1000:
            print("----- ON SCREEN DUMP START -----")
            print(f"only_boss_and_player={only_boss_and_player}")
            print(f"active_enemies_count={len(active_enemies)} total_enemies_count={len(enemies)}")

            for i, e in enumerate(enemies):
                print(
                    f"[ENEMY {i}] type={type(e).__name__} name={getattr(e, 'name', None)} "
                    f"is_active={getattr(e, 'is_active', None)} x={getattr(e, 'x', None)} y={getattr(e, 'y', None)} "
                    f"w={getattr(e, 'width', None)} h={getattr(e, 'height', None)} hp={getattr(e, 'enemyHealth', None)}"
                )

            if player is None:
                print("[PLAYER] None")
            else:
                print(
                    f"[PLAYER] type={type(player).__name__} "
                    f"x={getattr(player, 'x', None)} y={getattr(player, 'y', None)} "
                    f"w={getattr(player, 'width', None)} h={getattr(player, 'height', None)} "
                    f"hp={getattr(player, 'hp', None)}"
                )

            print("----- ON SCREEN DUMP END -----")
            self._debug_last_print = now

        self.boss_alone = only_boss_and_player

        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = getattr(GlobalConstants, "GAMEPLAY_HEIGHT", GlobalConstants.BASE_WINDOW_HEIGHT)

        if player is None:
            return

        # -------------------------
        # HARD WALL-ESCAPE (fix left-stick)
        # -------------------------
        if not hasattr(self, "_wall_escape_until"):
            self._wall_escape_until = 0
            self._wall_escape_dir = 0  # -1 = force left, +1 = force right
            self._wall_escape_zig = 1

        wall_threshold = self.edge_padding + 2  # pixels
        if self.x <= wall_threshold:
            self._wall_escape_until = now + 900
            self._wall_escape_dir = 1
            self._wall_escape_zig = random.choice([-1, 1])
        elif self.x + self.width >= (window_width - self.edge_padding - 2):
            self._wall_escape_until = now + 900
            self._wall_escape_dir = -1
            self._wall_escape_zig = random.choice([-1, 1])

        # -------------------------
        # STUCK DETECTION (time-based)
        # -------------------------
        if not hasattr(self, "_last_x"):
            self._last_x, self._last_y = self.x, self.y
            self._stuck_ms = 0
            self._last_stuck_check_time = now
            self._recovery_mode = False
            self._recovery_dir = (0, 0)
            self._recovery_end_time = 0

        dt = now - self._last_stuck_check_time
        self._last_stuck_check_time = now

        moved = (abs(self.x - self._last_x) >= 1.0) or (abs(self.y - self._last_y) >= 1.0)

        if not moved:
            self._stuck_ms += dt
        else:
            self._stuck_ms = 0
            if now > self._recovery_end_time:
                self._recovery_mode = False

        self._last_x, self._last_y = self.x, self.y

        if self._stuck_ms >= 250 and not self._recovery_mode:
            self._recovery_mode = True
            self._recovery_dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

            # If hugging left wall, force right recovery (primary fix)
            if self.x <= wall_threshold:
                self._recovery_dir = (1, 0)
            elif self.x + self.width >= (window_width - self.edge_padding - 2):
                self._recovery_dir = (-1, 0)

            self._recovery_end_time = now + 650

        # -------------------------
        # MOVEMENT DECISION
        # -------------------------
        # 1) wall-escape overrides everything
        if now < self._wall_escape_until:
            if self._wall_escape_dir == 1:
                self.mover.enemy_move_right(self)
            elif self._wall_escape_dir == -1:
                self.mover.enemy_move_left(self)

            # add small vertical wobble so we don't keep colliding in the same seam
            if hasattr(self.mover, "enemy_move_up") and hasattr(self.mover, "enemy_move_down"):
                if self._wall_escape_zig > 0:
                    self.mover.enemy_move_down(self)
                else:
                    self.mover.enemy_move_up(self)

            self._stuck_ms = 0

        # 2) recovery
        elif self._recovery_mode:
            dx, dy = self._recovery_dir
            if dx == 1:
                self.mover.enemy_move_right(self)
            elif dx == -1:
                self.mover.enemy_move_left(self)

            if dy == 1 and hasattr(self.mover, "enemy_move_down"):
                self.mover.enemy_move_down(self)
            elif dy == -1 and hasattr(self.mover, "enemy_move_up"):
                self.mover.enemy_move_up(self)

            if now > self._recovery_end_time:
                self._recovery_mode = False

        # 3) chase when not alone
        elif not self.boss_alone:
            if player.x > self.x:
                self.mover.enemy_move_right(self)
            elif player.x < self.x:
                self.mover.enemy_move_left(self)

        # 4) flee + zigzag when alone
        else:
            if not hasattr(self, "_zigzag_dir"):
                self._zigzag_dir = random.choice([-1, 1])
            if not hasattr(self, "_zigzag_toggle_ms"):
                self._zigzag_toggle_ms = 250
            if not hasattr(self, "_zigzag_last_toggle"):
                self._zigzag_last_toggle = now

            if now - self._zigzag_last_toggle >= self._zigzag_toggle_ms:
                self._zigzag_dir *= -1
                self._zigzag_last_toggle = now

            if player.x >= self.x:
                self.mover.enemy_move_left(self)
            else:
                self.mover.enemy_move_right(self)

            if hasattr(self.mover, "enemy_move_up") and hasattr(self.mover, "enemy_move_down"):
                if self._zigzag_dir > 0:
                    self.mover.enemy_move_down(self)
                else:
                    self.mover.enemy_move_up(self)
            else:
                self.y += self._zigzag_dir * float(self.moveSpeed)

        # -------------------------
        # BOUNDARY CLAMP
        # -------------------------
        if self.x < self.edge_padding:
            self.x = self.edge_padding
            # if we clamp on left, force a wall-escape immediately
            self._wall_escape_until = now + 900
            self._wall_escape_dir = 1
            self._wall_escape_zig = random.choice([-1, 1])

        elif self.x + self.width > window_width - self.edge_padding:
            self.x = window_width - self.edge_padding - self.width
            self._wall_escape_until = now + 900
            self._wall_escape_dir = -1
            self._wall_escape_zig = random.choice([-1, 1])

        if self.y < 0:
            self.y = 0
            if hasattr(self, "_zigzag_dir"):
                self._zigzag_dir *= -1
            if now < self._wall_escape_until:
                self._wall_escape_zig *= -1

        elif self.y + self.height > window_height:
            self.y = window_height - self.height
            if hasattr(self, "_zigzag_dir"):
                self._zigzag_dir *= -1
            if now < self._wall_escape_until:
                self._wall_escape_zig *= -1

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

    # def clamp_vertical(self) -> None:
    #     pass
