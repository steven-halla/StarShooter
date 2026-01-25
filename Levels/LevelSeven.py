import random
import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelSeven import BossLevelSeven
from SaveStates.SaveState import SaveState
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen
from Weapons.Bullet import Bullet

###
# Everytime we do a loop lets put more flames then
###

class LevelSeven(VerticalBattleScreen):
    def __init__(self, textbox):
        super().__init__(textbox)
        self.level_start: bool = True
        self.move_boss:bool = False
        self.tiled_map = pytmx.load_pygame(
            "./Levels/MapAssets/leveltmxfiles/level7.tmx"
        )
        self.tile_size = self.tiled_map.tileheight
        self.map_height_tiles = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400
        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - window_height
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame = 1.2
        self.save_state = SaveState()
        self.last_flame_row_time = pygame.time.get_ticks()
        self.flame_rows: list[list[Bullet]] = []
        self.level_start_time = pygame.time.get_ticks()
        self.napalm_list: list = []
        self.boss_shift_start_time: int | None = None
        self.boss_shift_done: bool = False
        self.flame_rects: list[pygame.Rect] = []
        self.flame_rows_built = 0
        self.max_flame_rows = 8
        self.flame_row_interval_ms = 60000
        self.last_flame_row_time = pygame.time.get_ticks()
        self.flame_base_world_y = None  # 🔒 STABLE WORLD ANCHOR
        self.boss_shift_start_time: int | None = None
        self.boss_shift_done: bool = False
        self.boss_teleport_x = 2000
        self.boss_teleport_y = 500
        self.boss_shift_done = True
        self.boss_shift_start_time = None
        self.start_loop: bool = False
        self.end_loop: bool = False
        self.boss_placement:bool = False

    def start(self, state) -> None:
        player_x = None
        player_y = None

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break
        self.starship = state.starship
        self.starship.x = player_x
        self.starship.y = player_y
        self.load_enemy_into_list(state)
        self.build_flame_grid()
        self.save_state.capture_player(self.starship, self.__class__.__name__)
        self.save_state.save_to_file("player_save.json")

    def update(self, state) -> None:
        super().update(state)
        self.update_loop_level(state)
        self.update_build_flame_row()
        self.update_enemy_helper(state)
        self.update_repeat_map(state)
        self.update_debug_print_player_and_boss_visible(state)

    def draw(self, state):
        super().draw(state)
        self.draw_player_and_enemies(state)
        self.draw_flames(state.DISPLAY, self.camera)
        self.draw_ui_panel(state.DISPLAY)
        pygame.display.flip()

    def update_build_flame_row(self):
        # This method is now disabled as flame rows are added when a loop is completed
        # Keeping the method for compatibility with existing code
        pass

    def update_loop_level(self, state):
        if self.camera.y <= 0 and not self.start_loop:
            self.start_loop = True
            self.end_loop = False

            # Add a new row of flames when a loop starts
            if self.flame_rows_built < self.max_flame_rows:
                self.flame_rows_built += 1
                self.build_flame_grid()
                print(f"Added flame row #{self.flame_rows_built} at loop start")

            if not self.boss_placement:
                self.set_boss_position_once(state)

        elif self.camera.y > 200 and not self.end_loop:
            self.end_loop = True
            self.start_loop = False
            self.boss_placement = False  # Reset the boss placement flag when the loop ends
            print("END LOOP")

    def update_enemy_helper(self, state):
        for enemy in list(state.enemies):
            result = enemy.update(state)

            if hasattr(enemy, "update_hitbox"):
                enemy.update_hitbox()

            if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                state.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            if result is not None:
                state.enemy_bullets.append(result)

            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)

                if not self.starship.invincible:
                    self.starship.shipHealth -= getattr(enemy, "contact_damage", 10)
                    self.starship.on_hit()
            else:
                enemy.color = GlobalConstants.RED
            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

    def update_repeat_map(self, state) -> None:
        map_height = self.map_height_tiles * self.tile_size
        if self.camera.y <= 0:
            wrap_offset = map_height
            self.camera.y += wrap_offset
            self.camera_y = self.camera.y
            self.starship.y += wrap_offset
            self.starship.update_hitbox()

            boss = next(
                (e for e in state.enemies if isinstance(e, BossLevelSeven)),
                None
            )

            if boss:
                self.respawn_boss_at_random_tile(boss)
                self.boss_shift_start_time = None
            boss = next(
                (e for e in state.enemies if isinstance(e, BossLevelSeven)),
                None
            )

            if boss:
                self.respawn_boss_at_random_tile(boss)
                self.boss_shift_start_time = None

    def update_move_map_y_axis(self):
        window_height = GlobalConstants.GAMEPLAY_HEIGHT

        self.camera_y -= self.map_scroll_speed_per_frame * 1.5

        max_camera_y = self.WORLD_HEIGHT - window_height
        if max_camera_y < 0:
            max_camera_y = 0

        if self.camera_y < 0:
            self.camera_y = 0
        elif self.camera_y > max_camera_y:
            self.camera_y = max_camera_y

        self.camera.y = float(self.camera_y)

    def update_debug_print_player_and_boss_visible(self, state) -> None:
        now = pygame.time.get_ticks()
        boss = next(
            (e for e in state.enemies if isinstance(e, BossLevelSeven)),
            None
        )

        if boss is None:
            self.boss_shift_start_time = None
            return

        player_on_screen = self.is_rect_on_screen(
            self.starship.x,
            self.starship.y,
            self.starship.width,
            self.starship.height,
        )

        boss_on_screen = self.is_rect_on_screen(
            boss.x,
            boss.y,
            boss.width,
            boss.height,
        )

        if player_on_screen and boss_on_screen:
            if self.boss_shift_start_time is None:
                self.boss_shift_start_time = now

            elapsed = now - self.boss_shift_start_time

            if elapsed >= 10000:
                self.respawn_boss_at_random_tile(boss)
                self.boss_shift_done = True
                self.boss_shift_start_time = None
                print("[BOSS VANISHED]")
        else:
            self.boss_shift_start_time = None

    def draw_static_bullets(
            self,
            bullets: list[Bullet],
            surface: pygame.Surface
    ) -> None:
        for bullet in bullets:
            bullet.draw(surface)

    def draw_flames(self, surface: pygame.Surface, camera) -> None:
        if not self.flame_rects:
            return

        color = (255, 165, 0)
        z = camera.zoom
        player_hitbox = self.starship.hitbox
        player_screen_rect = pygame.Rect(
            camera.world_to_screen_x(player_hitbox.x),
            camera.world_to_screen_y(player_hitbox.y),
            int(player_hitbox.width * z),
            int(player_hitbox.height * z),
        )

        for rect in self.flame_rects:
            if player_screen_rect.colliderect(rect):
                if not self.starship.invincible:
                    self.starship.shipHealth -= 20
                    self.starship.on_hit()
                print("🔥 PLAYER COLLIDED WITH ORANGE FLAME")

            pygame.draw.rect(surface, color, rect)

    def draw_flames_rect(self, state):
        for row in self.flame_rows:
            for flame in row:
                pygame.draw.rect(
                    state.DISPLAY,
                    (255, 100, 0),
                    pygame.Rect(
                        flame.x,
                        flame.y,
                        flame.width,
                        flame.height
                    )
                )

    def draw_player_and_enemies(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for boss in state.enemies:
            if not isinstance(boss, BossLevelSeven):
                continue
            boss.draw(state.DISPLAY, self.camera)
            boss.draw_damage_flash(state.DISPLAY, self.camera)

    def draw_level_collision(self, surface: pygame.Surface) -> None:
        self.draw_collision_tiles(surface)

    def build_flame_row(self) -> None:
        SIZE = 82
        GAP = 6
        START_X = 8
        COLS = 9

        if self.flame_rows_built >= self.max_flame_rows:
            return

        if self.flame_base_world_y is None:
            self.flame_base_world_y = (
                    self.camera.y
                    + (self.camera.window_height / self.camera.zoom)
                    - SIZE
            )

        row_offset_y = -(self.flame_rows_built * (SIZE + GAP))

        for col in range(COLS):
            x = START_X + col * (SIZE + GAP)
            y = self.flame_base_world_y + row_offset_y
            self.flame_rects.append(pygame.Rect(x, y, SIZE, SIZE))

        self.flame_rows_built += 1

    def is_rect_on_screen(self, x: float, y: float, w: int, h: int) -> bool:
        visible_left = self.camera.x
        visible_top = self.camera.y
        visible_right = self.camera.x + (self.window_width / self.camera.zoom)
        visible_bottom = self.camera.y + (self.window_height / self.camera.zoom)

        if x + w < visible_left:
            return False
        if x > visible_right:
            return False
        if y + h < visible_top:
            return False
        if y > visible_bottom:
            return False
        return True

    def teleport_boss_to_new_point(self) -> None:
        coords: list[tuple[int, int]] = []
        for layer in self.tiled_map.layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "boss_appear_point":
                for x, y, gid in layer:
                    if gid == 0:
                        continue
                    world_x = x * self.tile_size
                    world_y = y * self.tile_size
                    coords.append((world_x, world_y))

    def load_enemy_into_list(self, state) -> None:
        state.enemies.clear()
        try:
            layer = self.tiled_map.get_layer_by_name("boss_appear_point")
        except ValueError:
            print("[LEVEL 7] No tile layer named 'boss_appear_point'")
            return

        spawn_tiles: list[tuple[int, int]] = [
            (tx, ty) for tx, ty, gid in layer if gid != 0
        ]

        if not spawn_tiles:
            print("[LEVEL 7] 'boss_appear_point' layer has no tiles set")
            return

        tx, ty = max(spawn_tiles, key=lambda t: t[1])
        tile_world_x = tx * self.tile_size
        tile_world_y = ty * self.tile_size
        boss = BossLevelSeven()
        boss.x = tile_world_x + (self.tile_size - boss.width) // 2
        boss.y = tile_world_y + (self.tile_size - boss.height) // 2
        boss.camera = self.camera
        boss.target_player = self.starship
        boss.update_hitbox()
        state.enemies.append(boss)

        print("[LEVEL 7] boss_appear_point tiles (world):")
        for sx, sy in spawn_tiles:
            print(f"  tile -> ({sx * self.tile_size}, {sy * self.tile_size})")

        print(f"[LEVEL 7] Boss spawned world: ({boss.x}, {boss.y})")
        print(
            f"[LEVEL 7] Boss spawned SCREEN: "
            f"({self.camera.world_to_screen_x(boss.x)}, "
            f"{self.camera.world_to_screen_y(boss.y)})"
        )

    def build_flame_grid(self) -> None:
        SIZE = 82
        GAP = 6
        START_X = 8
        COLS = 9

        self.flame_rects.clear()

        screen_height = GlobalConstants.GAMEPLAY_HEIGHT

        for row in range(self.flame_rows_built):
            row_y = screen_height - SIZE - row * (SIZE + GAP)
            for col in range(COLS):
                x = START_X + col * (SIZE + GAP)
                self.flame_rects.append(pygame.Rect(x, row_y, SIZE, SIZE))

    def respawn_boss_at_random_tile(self, boss) -> None:
        try:
            layer = self.tiled_map.get_layer_by_name("boss_appear_point")
        except ValueError:
            return

        spawn_tiles: list[tuple[int, int]] = []
        for tx, ty, gid in layer:
            if gid != 0:
                spawn_tiles.append((tx, ty))

        if not spawn_tiles:
            return

        tx, ty = random.choice(spawn_tiles)
        boss.x = tx * self.tile_size + (self.tile_size - boss.width) // 2
        boss.y = ty * self.tile_size + (self.tile_size - boss.height) // 2
        boss.update_hitbox()

    def set_boss_position_once(self, state) -> None:

        boss = next(
            (e for e in state.enemies if isinstance(e, BossLevelSeven)),
            None
        )
        if boss:
            self.respawn_boss_at_random_tile(boss)
            self.boss_placement = True
        else:
            print("No BossLevelSeven found in enemies list")
