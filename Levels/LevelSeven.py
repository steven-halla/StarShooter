import random

import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Bosses.BossLevelSeven import BossLevelSeven
from SaveStates.SaveState import SaveState
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen
from Weapons.Weapon import Weapon

UI_HEIGHT = 0
BULLET_SIZE = 64
NUM_BULLETS = 10
BULLET_DAMAGE = 30



# INCLUDE GATES TO MAKE CERTAIN PARTS OF MAP NONE ASSEBIBLE OVER TIME


class LevelSeven(VerticalBattleScreen):
    def __init__(self, textbox):
        super().__init__(textbox)

        self.bossLevelSevenGroup: list[BossLevelSeven] = []
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

        self.map_scroll_speed_per_frame = 0.4

        self.save_state = SaveState()

        self.last_flame_row_time = pygame.time.get_ticks()

        self.flame_rows: list[list[Weapon]] = []
        self.level_start_time = pygame.time.get_ticks()
        # LevelSeven.__init__()

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

        # Optional explicit teleport target (leave as None to use x+300)

        self.boss_teleport_x = 2000  # whatever absolute world X works with your clamp
        self.boss_teleport_y = 500  # whatever absolute world Y you want
        self.boss_shift_done = True
        self.boss_shift_start_time = None  # ⛔ stop timer
    # -------------------------------------------------
    # FLAMES
    # -------------------------------------------------
    # def add_flame_row(self) -> None:
    #     print("🔥 add_flame_row fired")
    #
    #     FLAME_SIZE = 64
    #     DAMAGE = 30
    #
    #     row_index = len(self.flame_rows)
    #
    #     if row_index >= len(FLAME_POSITIONS):
    #         print("🔥 No more rows")
    #         return
    #
    #     row: list[Weapon] = []
    #
    #     for x, y in FLAME_POSITIONS[row_index]:
    #         flame = Weapon(x, y)
    #         flame.width = FLAME_SIZE
    #         flame.height = FLAME_SIZE
    #         flame.damage = DAMAGE
    #         flame.speed = 0
    #         flame.dx = 0
    #         flame.update_rect()
    #
    #         print(f"🔥 Flame created at {x}, {y}")
    #         row.append(flame)
    #
    #     self.flame_rows.append(row)

    # def create_static_bottom_bullets(self, screen_width: int, screen_height: int):
    #     bullets = []
    #
    #     spacing = screen_width // NUM_BULLETS
    #     y = screen_height - UI_HEIGHT - BULLET_SIZE
    #
    #     for i in range(NUM_BULLETS):
    #         x = i * spacing + (spacing - BULLET_SIZE) // 2
    #         bullet = Weapon(x, y)
    #         bullet.width = BULLET_SIZE
    #         bullet.height = BULLET_SIZE
    #         bullet.update_rect()
    #         bullets.append(bullet)
    #
    #     return bullets

    def clear_all_enemy_groups(self) -> None:
        self.bileSpitterGroup.clear()
        self.kamikazeDroneGroup.clear()
        self.triSpitterGroup.clear()
        self.waspStingerGroup.clear()
        self.bladeSpinnerGroup.clear()
        self.sporeFlowerGroup.clear()
        self.spineLauncherGroup.clear()
        self.acidLauncherGroup.clear()
        self.ravagerGroup.clear()
        self.fireLauncherGroup.clear()
        self.transportWormGroup.clear()
        self.spinalRaptorGroup.clear()
        self.slaverGroup.clear()
        self.coinsGroup.clear()
        self.spikeyBallGroup.clear()



    def start(self, state) -> None:

        player_x = None
        # self.textbox.show(self.intro_dialogue)
        player_y = None

        # self.static_bullets = self.create_static_bottom_bullets(
        #     GlobalConstants.BASE_WINDOW_WIDTH,
        #     GlobalConstants.GAMEPLAY_HEIGHT
        # )

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break
        self.starship = state.starship

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()
        # self.starship.x = player_x
        # self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list()

    def move_map_y_axis(self):
        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = GlobalConstants.GAMEPLAY_HEIGHT

        # move camera UP in world space (so map scrolls down)
        self.camera_y -= self.map_scroll_speed_per_frame * 1.5

        # clamp so we never scroll past top or bottom of the map
        max_camera_y = self.WORLD_HEIGHT - window_height
        if max_camera_y < 0:
            max_camera_y = 0

        if self.camera_y < 0:
            self.camera_y = 0
        elif self.camera_y > max_camera_y:
            self.camera_y = max_camera_y

        # keep Camera object in sync
        self.camera.y = float(self.camera_y)


    def update(self, state) -> None:
        super().update(state)

        if self.bossLevelSevenGroup:
            boss = self.bossLevelSevenGroup[0]
            # print(f"Boss world position: ({boss.x}, {boss.y})")
        else:
            print("No boss in bossLevelSevenGroup")
        # self.update_static_bullets(self.static_bullets, self.starship.hitbox)
        now = pygame.time.get_ticks()

        now = pygame.time.get_ticks()

        if (
                self.flame_rows_built < self.max_flame_rows
                and now - self.last_flame_row_time >= self.flame_row_interval_ms
        ):
            self.flame_rows_built += 1
            self.last_flame_row_time = now
            self.build_flame_grid()


        # print("=== ENEMY LIST ===")
        # print(f"BileSpitter: {len(self.bileSpitterGroup)}")
        # print(f"TriSpitter: {len(self.triSpitterGroup)}")
        # print(f"BladeSpinner: {len(self.bladeSpinnerGroup)}")
        # print(f"BossLevelOne: {len(self.bossLevelOneGroup)}")
        # print(
        #     f"TOTAL: "
        #     f"{len(self.bileSpitterGroup) + len(self.triSpitterGroup) + len(self.bladeSpinnerGroup) + len(self.bossLevelOneGroup)}"
        # )
        # print("==================")
        # if len(self.missed_enemies) > 9:
        #     print("GAME OVER!!!")
        #     self.game_over = True

        if self.level_start == True:
            self.level_start = False
            self.starship.shipHealth = 244
            self.clear_all_enemy_groups()
            self.build_flame_grid()
            self.save_state.capture_player(self.starship, self.__class__.__name__)
            self.save_state.save_to_file("player_save.json")

        # FIX: use the attribute that already exists

        now = pygame.time.get_ticks()
        elapsed = now - self.level_start_time
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)




        # if elapsed >= self.time_limit_ms and not self.time_up:
        #     self.time_up = True
        #     print("time's up")
        # Missile firing (override parent behavior)
        if self.controller.fire_missiles:
            missile = self.starship.fire_missile()
            if missile is not None:

                # Lock onto nearest enemy
                missile.target_enemy = self.get_nearest_enemy(missile)

                # Compute initial direction toward target
                if missile.target_enemy is not None:
                    dx = missile.target_enemy.x - missile.x
                    dy = missile.target_enemy.y - missile.y
                    dist = max(1, (dx * dx + dy * dy) ** 0.5)
                    missile.direction_x = dx / dist
                    missile.direction_y = dy / dist
                else:
                    # No enemy → missile goes straight upward
                    missile.direction_x = 0
                    missile.direction_y = -1

                # Add to missile list
                self.player_missiles.append(missile)

                # if missile.target_enemy is not None:
                #     print(f"Missile locked onto: {type(missile.target_enemy).__name__} "
                #           f"at ({missile.target_enemy.x}, {missile.target_enemy.y})")
                # else:
                #     print("Missile locked onto: NONE (no enemies found)")

        self.enemy_helper()
        # if not self.bossLevelSevenGroup and not self.level_complete:
        #     self.level_complete = True


        self.extract_object_names()
        # if self.level_complete:
        #
        #     next_level = MissionBriefingScreenLevelTwo()
        #     # next_level.set_player(state.starship)
        #     state.currentScreen = next_level
        #     next_level.start(state)
        #     print(type(state.currentScreen).__name__)
        #
        #     return

        self.repeat_map()

        # debug print
        self.debug_print_player_and_boss_visible()

        self.move_map_y_axis()

        # self.update_collision_tiles(damage=5)


        self.repeat_map()


    def draw_level_collision(self, surface: pygame.Surface) -> None:
        self.draw_collision_tiles(surface)

    def draw(self, state):
        super().draw(state)
        # ================================
        # ENEMY COUNTER (TOP OF SCREEN)
        # ================================
        font = pygame.font.Font(None, 28)

        current_enemies = (

                + len(self.bossLevelSevenGroup)
        )
        # print(current_enemies)
        # initialize on first frame



        for napalm in self.napalm_list:
            napalm.draw(state.DISPLAY, self.camera)
        zoom = self.camera.zoom

        # for obj in self.tiled_map.objects:
        #     if hasattr(obj, "image") and obj.image is not None:
        #         screen_x = self.camera.world_to_screen_x(obj.x)
        #         screen_y = self.camera.world_to_screen_y(obj.y)
        #         state.DISPLAY.blit(obj.image, (screen_x, screen_y))

        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)


        for boss in self.bossLevelSevenGroup:
            boss.draw(state.DISPLAY, self.camera)
            boss.draw_damage_flash(state.DISPLAY, self.camera)

        # self.draw_static_bullets(self.static_bullets, state.DISPLAY)


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

        # inside LevelSeven.draw(self, state)

        # AFTER map / background draw
        # BEFORE UI draw

        # self.draw_flames(state.DISPLAY, self.camera)
        self.draw_ui_panel(state.DISPLAY)
        # self.textbox.show("I am the ultimate man on the battlefiled. You cannot hope to win aginst the likes of me, prepare yourself dum dum mortal head. bla bla bal bal bla; win  the likes of me, prepare yourself dum dum mortal head. bla bla bal bal bla")

        # self.textbox.draw(state.DISPLAY)


        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        enemies = (
                list(self.bossLevelSevenGroup)
        )

        if not enemies:
            return None

        # Visible camera bounds (world coordinates)
        visible_top = self.camera.y
        visible_bottom = self.camera.y + (self.window_height / self.camera.zoom)

        nearest_enemy = None
        nearest_dist = float("inf")
        mx, my = missile.x, missile.y

        for enemy in enemies:

            # ⛔ Skip enemies outside the screen
            if enemy.y + enemy.height < visible_top:
                continue  # enemy is above screen
            if enemy.y > visible_bottom:
                continue  # enemy is below screen

            # distance calculation
            dx = enemy.x - mx
            dy = enemy.y - my
            dist_sq = dx * dx + dy * dy

            if dist_sq < nearest_dist:
                nearest_dist = dist_sq
                nearest_enemy = enemy

        return nearest_enemy

    def extract_object_names(self) -> list[str]:
        """
        Returns a list of all object.name strings found in the Tiled map.
        """
        names = []

        for obj in self.tiled_map.objects:
            if hasattr(obj, "name") and obj.name:
                names.append(obj.name)
        # print(names)
        return names

    def load_enemy_into_list(self) -> None:
        self.bossLevelSevenGroup.clear()

        # --- get the tile layer named "boss_appear_point" ---
        try:
            layer = self.tiled_map.get_layer_by_name("boss_appear_point")
        except ValueError:
            print("[LEVEL 7] No tile layer named 'boss_appear_point'")
            return

        # collect ALL boss_appear_point tiles
        spawn_tiles: list[tuple[int, int]] = []
        for tx, ty, gid in layer:
            if gid != 0:
                spawn_tiles.append((tx, ty))

        if not spawn_tiles:
            print("[LEVEL 7] 'boss_appear_point' layer has no tiles set")
            return

        # pick the BOTTOM-MOST tile (largest ty)
        tx, ty = max(spawn_tiles, key=lambda t: t[1])

        tile_world_x = tx * self.tile_size
        tile_world_y = ty * self.tile_size

        boss = BossLevelSeven()
        boss_width = boss.width
        boss_height = boss.height

        # center boss on that tile
        boss.x = tile_world_x + (self.tile_size - boss_width) // 2
        boss.y = tile_world_y + (self.tile_size - boss_height) // 2

        boss.update_hitbox()
        boss.camera = self.camera
        boss.target_player = self.starship
        self.bossLevelSevenGroup.append(boss)

        # debug prints
        print("[LEVEL 7] boss_appear_point tiles (world):")
        for sx, sy in spawn_tiles:
            print(f"  tile -> ({sx * self.tile_size}, {sy * self.tile_size})")

        print(f"[LEVEL 7] Boss spawned world: ({boss.x}, {boss.y})")

        # also show where that is on SCREEN to verify visibility
        sx = self.camera.world_to_screen_x(boss.x)
        sy = self.camera.world_to_screen_y(boss.y)
        print(f"[LEVEL 7] Boss spawned SCREEN: ({sx}, {sy})")



    def enemy_helper(self):



        # screen bottom in WORLD coordinates
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        # -------------------------
        # NAPALM UPDATE + DAMAGE
        # -------------------------
        for napalm in list(self.napalm_list):
            napalm.update()

            if napalm.is_active and napalm.hits(self.starship.hitbox):
                if not self.starship.invincible:
                    self.starship.shipHealth -= napalm.damage
                    self.starship.on_hit()

            if not napalm.is_active:
                self.napalm_list.remove(napalm)

        # -------------------------
        # METAL SHIELD → ENEMY BULLETS
        # -------------------------
        for metal in list(self.metal_shield_bullets):

            if not metal.is_active:
                self.metal_shield_bullets.remove(metal)
                continue

            shield_rect = pygame.Rect(
                metal.x,
                metal.y,
                metal.width,
                metal.height
            )

            for bullet in list(self.enemy_bullets):
                if bullet.collide_with_rect(shield_rect):

                    absorbed = metal.absorb_hit()

                    if bullet in self.enemy_bullets:
                        self.enemy_bullets.remove(bullet)

                    if absorbed and metal in self.metal_shield_bullets:
                        self.metal_shield_bullets.remove(metal)

                    break

        # -------------------------
        # BOSS
        # -------------------------
        for boss in list(self.bossLevelSevenGroup):



            boss.update()
            # ❌ DO NOT REMOVE BOSS FROM GROUP
            # keep boss alive until HP <= 0
            if boss.enemyHealth <= 0:
                print("[BOSS DEAD] level complete")
                self.level_complete = True

            if boss.enemyBullets:
                self.enemy_bullets.extend(boss.enemyBullets)
                boss.enemyBullets.clear()

            if boss.enemyHealth <= 0:
                self.bossLevelSevenGroup.remove(boss)
                print("level complete")

    def repeat_map(self) -> None:
        """
        Seamlessly wrap the map vertically when the camera reaches the top,
        keeping player motion smooth (no snap / no visible jump).
        """

        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        map_height = self.map_height_tiles * self.tile_size

        # when camera scrolls past the top, wrap
        if self.camera.y <= 0:

            wrap_offset = map_height

            # shift camera down by one full map height
            self.camera.y += wrap_offset
            self.camera_y = self.camera.y

            # shift player down by same amount (preserves relative position)
            self.starship.y += wrap_offset
            self.starship.update_hitbox()

            # shift all world entities down
            for group in (
                    self.coinsGroup,
                    self.spikeyBallGroup,
                    self.bossLevelSixGroup,
            ):
                for enemy in group:
                    enemy.y += wrap_offset
                    enemy.update_hitbox()

                    # Static bottom bullets using Weapon

    # def update_static_bullets(self, bullets: list[Weapon], player_hitbox: pygame.Rect) -> None:
    #
    #     player_screen_rect = pygame.Rect(
    #         self.camera.world_to_screen_x(player_hitbox.x),
    #         self.camera.world_to_screen_y(player_hitbox.y),
    #         player_hitbox.width,
    #         player_hitbox.height
    #     )
    #
    #     for bullet in bullets:
    #         if bullet.rect.colliderect(player_screen_rect):
    #             self.starship.shipHealth -= BULLET_DAMAGE
    #             print("Player bullet collision")

    def draw_static_bullets(
            self,
            bullets: list[Weapon],
            surface: pygame.Surface
    ) -> None:
        for bullet in bullets:
            bullet.draw(surface)

    # BUILD — WORLD SPACE ONLY (NO CAMERA)
    # BUILD — WORLD Y LOCKED TO SCREEN BOTTOM (LEVEL 6 PATTERN)
    # PROBLEM:
    # You are overwriting rect.y every frame in draw_flames,
    # so ALL rows collapse into ONE row.

    # FIX:
    # Encode row offset into the RECT ITSELF.
    # draw_flames must NOT change rect.y per-rect.

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

    def draw_flames(self, surface: pygame.Surface, camera) -> None:
        if not self.flame_rects:
            return

        color = (255, 165, 0)

        # player in SCREEN space
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
    def build_flame_row(self) -> None:
        SIZE = 82
        GAP = 6
        START_X = 8
        COLS = 9

        if self.flame_rows_built >= self.max_flame_rows:
            return

        # 🔒 anchor ONCE
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

    def _is_rect_on_screen(self, x: float, y: float, w: int, h: int) -> bool:
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

    def debug_print_player_and_boss_visible(self) -> None:
        now = pygame.time.get_ticks()

        # -------------------------
        # ALWAYS PRINT TIMER STATE
        # -------------------------
        if self.boss_shift_start_time is None:
            print(f"[BOSS TIMER] state=IDLE boss_shift_done={self.boss_shift_done} elapsed=0")
        else:
            print(
                f"[BOSS TIMER] state=RUNNING boss_shift_done={self.boss_shift_done} "
                f"elapsed={now - self.boss_shift_start_time}"
            )

        # -------------------------
        # NO BOSS → TIMER MUST NOT RUN
        # -------------------------
        if not self.bossLevelSevenGroup:
            self.boss_shift_start_time = None
            return

        boss = self.bossLevelSevenGroup[0]

        player_on_screen = self._is_rect_on_screen(
            self.starship.x,
            self.starship.y,
            self.starship.width,
            self.starship.height,
        )

        boss_on_screen = self._is_rect_on_screen(
            boss.x,
            boss.y,
            boss.width,
            boss.height,
        )

        # -------------------------
        # START TIMER ONLY WHEN BOTH VISIBLE
        # -------------------------
        if player_on_screen and boss_on_screen:
            if self.boss_shift_start_time is None:
                self.boss_shift_start_time = now

            elapsed = now - self.boss_shift_start_time

            # -------------------------
            # VANISH AFTER 3 SECONDS
            # -------------------------
            # if elapsed >= 3000:
            #     boss.x = self.boss_teleport_x
            #     boss.y = self.boss_teleport_y
            #     boss.update_hitbox()
            #
            #     self.boss_shift_done = True
            #     self.boss_shift_start_time = None
            #     print("[BOSS VANISHED]")

            if elapsed >= 3000:
                self.respawn_boss_at_random_tile(boss)
                self.boss_shift_done = True
                self.boss_shift_start_time = None
                print("[BOSS VANISHED]")

        else:
            # -------------------------
            # VISIBILITY LOST → STOP TIMER
            # -------------------------
            self.boss_shift_start_time = None

    def teleport_boss_to_new_point(self) -> None:
        """
        Debug helper.
        Print the world coords of every tile in the 'boss_appear_point' tile layer.
        """
        coords: list[tuple[int, int]] = []

        for layer in self.tiled_map.layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "boss_appear_point":
                for x, y, gid in layer:
                    if gid == 0:
                        continue

                    world_x = x * self.tile_size
                    world_y = y * self.tile_size
                    coords.append((world_x, world_y))

        # for (wx, wy) in coords:
        #     print(f"boss_appear_point tile world coord: ({wx}, {wy})")
        #
        # print(f"TOTAL boss_appear_point tiles found: {len(coords)}")

    # ADD THIS METHOD (NO UNDERSCORE)

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

    # REPLACE ONLY THIS PART INSIDE debug_print_player_and_boss_visible

