import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelFour import BossLevelFour
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.Slaver import Slaver
from Entity.Monsters.TransportWorm import TransportWorm
from Entity.Monsters.TriSpitter import TriSpitter
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen

class LevelFour(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        self.level_start = True
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level4.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        self.camera_y = self.WORLD_HEIGHT - window_height
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = .4
        self.napalm_list: list = []
        self.total_enemies = 40
        self.creep_last_spawn_time = 0
        self.prev_enemy_count: int = None
        self.worm_visible: bool = False
        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000
        self.time_up = False
        self.missed_enemies = []
        self.game_over: bool = False
        self.level_complete = False
        self.worms_saved: list = []
        self.touched_worms: list[TransportWorm] = []


    def start(self, state) -> None:
        print("Starting Level Four")
        self.starship = state.starship

        player_x = None
        player_y = None
        state.starship.current_level = 4

        for obj in self.tiled_map.objects:
            if obj.name == "player":
                player_x = obj.x
                player_y = obj.y
                break

        if "Napalm Spread" not in state.starship.magic_inventory:
            state.starship.magic_inventory.append("Napalm Spread")
        state.starship.equipped_magic = ["Napalm Spread", None]

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list(state)
        self.save_state.capture_player(self.starship)
        self.save_state.save_to_file("player_save.json")

    def update(self, state) -> None:
        super().update(state)
        active_worms, creep_found_on_screen, now, screen_left, screen_top = self.update_worm_helper(state)
        self.update_creep_helper(active_worms, creep_found_on_screen, now, screen_left, screen_top, state)

        if self.map_scroll_speed_per_frame == 0:
            for worm in active_worms:
                worm.update(state)
                # Ensure worms that were newly added to touched_worms are tracked
                if worm.is_active and worm not in self.touched_worms:
                    self.touched_worms.append(worm)

            for enemy in state.enemies:
                if isinstance(enemy, Slaver):
                    enemy.update(state)

        self.update_summon_enemies(active_worms, now, state)
        self.update_enemy_bullet_helper(state)
        self.update_enemy_helper(state)

    def draw(self, state):
        super().draw(state)
        self.draw_enemy_player(state)
        self.draw_ui_panel(state.DISPLAY)
        pygame.display.flip()

    def slaver_player_in_vicinity(self, slaver, state) -> bool:
        if slaver.camera is None or self.starship is None:
            return

        # ---- WORM VICINITY CHECK FIRST ----
        for e in state.enemies:
            if isinstance(e, TransportWorm):
                dx_w = abs(e.x - self.starship.x)
                dy_w = abs(e.y - self.starship.y)

                if dx_w <= 400 and dy_w <= 300:
                    return  # <-- exits immediately

        # ---- WORLD DISTANCE CHECK ----
        dx = abs(slaver.x - self.starship.x)
        dy = abs(slaver.y - self.starship.y)
        in_range = dx <= 400 and dy <= 300

        # ---- SCREEN VISIBILITY CHECK ----
        slaver_screen_y = self.camera.world_to_screen_y(slaver.y)
        player_screen_y = self.camera.world_to_screen_y(self.starship.y)

        slaver_visible = (
                slaver_screen_y + slaver.height >= 0 and
                slaver_screen_y <= self.camera.window_height
        )

        player_visible = (
                player_screen_y + self.starship.height >= 0 and
                player_screen_y <= self.camera.window_height
        )

        return in_range and slaver_visible and player_visible

    def update_enemy_helper(self, state):

        for enemy in list(state.enemies):
            # Transport worms are updated in the main update loop if map_scroll_speed_per_frame == 0
            if isinstance(enemy, TransportWorm) or isinstance(enemy, Slaver):
                if self.map_scroll_speed_per_frame == 0:
                    if hasattr(enemy, "update_hitbox"):
                        enemy.update_hitbox()

                    if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                        state.enemy_bullets.extend(enemy.enemyBullets)
                        enemy.enemyBullets.clear()

                    if enemy.enemyHealth <= 0:
                        state.enemies.remove(enemy)
                continue

            enemy.update(state)

            if hasattr(enemy, "update_hitbox"):
                enemy.update_hitbox()

            if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                state.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            if isinstance(enemy, Slaver):
                if self.slaver_player_in_vicinity(enemy, state):
                    enemy.attack_player = True
                    # print("SLAVER ATTACKING PLAYER")
                else:
                    enemy.attack_player = False
                    # print("SLAVER NOT ATTACKING PLAYER")


    def update_worm_helper(self, state):
        PADDING = 100
        now = pygame.time.get_ticks()

        player_screen_y = self.camera.world_to_screen_y(self.starship.y)
        player_screen_bottom = player_screen_y + self.starship.height

        player_visible = (
                player_screen_bottom >= PADDING
                and player_screen_y <= self.camera.window_height + PADDING
        )

        screen_left = self.camera.get_world_x_left()
        screen_top = self.camera.y

        active_worms = []

        for enemy in state.enemies:
            if not isinstance(enemy, TransportWorm):
                continue

            worm_screen_y = self.camera.world_to_screen_y(enemy.y)
            worm_screen_bottom = worm_screen_y + enemy.height

            worm_visible = (
                    worm_screen_bottom >= PADDING
                    and worm_screen_y <= self.camera.window_height + PADDING
            )

            if worm_visible:
                active_worms.append(enemy)

        # ===============================
        # FIXED SCROLL CONTROL LOGIC
        # ===============================

        # if player_visible and active_worms:
        #     print(">>> PLAYER AND WORM ON SCREEN <<<")
        #     self.map_scroll_speed_per_frame = 0.0
        #     self.camera.scroll_speed_per_frame = 0.0
        # else:
        #     # restore scrolling when no worms visible
        #     self.map_scroll_speed_per_frame = 0.4
        #     self.camera.scroll_speed_per_frame = 0.4

        # ===============================

        creep_found_on_screen = False

        if self.map_scroll_speed_per_frame == 0.0:
            try:
                creep_layer = self.tiled_map.get_layer_by_name("creep")
            except ValueError:
                creep_layer = None

            if creep_layer is not None:
                tile_w = self.tiled_map.tilewidth
                tile_h = self.tiled_map.tileheight

                screen_left = self.camera.get_world_x_left()
                screen_right = screen_left + (self.camera.window_width / self.camera.zoom)

                screen_top = self.camera.y
                screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

                start_x = int(screen_left // tile_w)
                end_x = int(screen_right // tile_w)
                start_y = int(screen_top // tile_h)
                end_y = int(screen_bottom // tile_h)

                for ty in range(start_y, end_y + 1):
                    if ty < 0 or ty >= len(creep_layer.data):
                        continue

                    for tx in range(start_x, end_x + 1):
                        if tx < 0 or tx >= len(creep_layer.data[ty]):
                            continue

                        if creep_layer.data[ty][tx] != 0:
                            creep_found_on_screen = True
                            break

                    if creep_found_on_screen:
                        break

        return active_worms, creep_found_on_screen, now, screen_left, screen_top

    def update_creep_helper(
            self,
            active_worms,
            creep_found_on_screen,
            now,
            screen_left,
            screen_top,
            state
    ):

        # --------------------------------------------------
        # VISIBILITY CHECKS
        # --------------------------------------------------
        player_screen_y = self.camera.world_to_screen_y(self.starship.y)
        player_screen_bottom = player_screen_y + self.starship.height

        player_visible = (
                player_screen_bottom >= 0 and
                player_screen_y <= self.camera.window_height
        )

        worm_visible = len(active_worms) > 0

        # --------------------------------------------------
        # CREEP DETECTION (RECALCULATED HERE)
        # --------------------------------------------------
        creep_found_on_screen = False
        creep_near_bottom = False

        try:
            creep_layer = self.tiled_map.get_layer_by_name("creep")
        except ValueError:
            creep_layer = None

        if creep_layer is not None:

            tile_w = self.tiled_map.tilewidth
            tile_h = self.tiled_map.tileheight

            screen_right = screen_left + (self.camera.window_width / self.camera.zoom)
            screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

            start_x = int(screen_left // tile_w)
            end_x = int(screen_right // tile_w)
            start_y = int(screen_top // tile_h)
            end_y = int(screen_bottom // tile_h)

            for ty in range(start_y, end_y + 1):
                if ty < 0 or ty >= len(creep_layer.data):
                    continue

                for tx in range(start_x, end_x + 1):
                    if tx < 0 or tx >= len(creep_layer.data[ty]):
                        continue

                    if creep_layer.data[ty][tx] != 0:

                        creep_found_on_screen = True

                        # Convert tile Y to world Y
                        creep_world_y = ty * tile_h
                        creep_screen_y = self.camera.world_to_screen_y(creep_world_y)

                        # Check if creep is within 100px of bottom
                        if creep_screen_y >= self.camera.window_height - 400:
                            creep_near_bottom = True

                        break

                if creep_found_on_screen:
                    break

        # --------------------------------------------------
        # DEBUG PRINT (YOU ASKED FOR THIS)
        # --------------------------------------------------
        print(
            "player_visible:", player_visible,
            "worm_visible:", worm_visible,
            "creep_found_on_screen:", creep_found_on_screen,
            "creep_near_bottom:", creep_near_bottom
        )

        # --------------------------------------------------
        # SCROLL CONTROL (CREEP DECIDES)
        # --------------------------------------------------
        if player_visible and worm_visible and creep_found_on_screen and creep_near_bottom:
            print(">>> CREEP PAUSE TRIGGERED <<<")
            self.map_scroll_speed_per_frame = 0.0
            self.camera.scroll_speed_per_frame = 0.0
        else:
            self.map_scroll_speed_per_frame = 0.4
            self.camera.scroll_speed_per_frame = 0.4

        # --------------------------------------------------
        # SPAWN SLAVER IF NEEDED
        # --------------------------------------------------
        if self.map_scroll_speed_per_frame == 0 and creep_found_on_screen and now - self.creep_last_spawn_time >= 5500:
            slaver = Slaver()
            slaver.x = screen_left
            slaver.y = screen_top
            slaver.width = 16
            slaver.height = 16
            slaver.camera = self.camera
            slaver.target_player = self.starship
            slaver.touched_worms = self.touched_worms
            slaver.transport_worms = active_worms
            slaver.update_hitbox()

            state.enemies.append(slaver)
            self.creep_last_spawn_time = now

    def update_summon_enemies(self, active_worms, now, state):
        if self.map_scroll_speed_per_frame != 0:
            return

        for worm in active_worms:
            if now - worm.last_summon_time >= worm.summon_interval_ms:
                worm.summon_enemy(
                    enemy_classes=[
                        BileSpitter,
                        KamikazeDrone,
                        TriSpitter,
                        FireLauncher,
                    ],
                    enemy_groups={
                        BileSpitter: state.enemies,
                        KamikazeDrone: state.enemies,
                        TriSpitter: state.enemies,
                        FireLauncher: state.enemies,
                    },
                    spawn_y_offset=20
                )
                worm.last_summon_time = now

    def update_enemy_bullet_helper(self, state):
        for enemy in list(state.enemies):

            if hasattr(enemy, "update_hitbox"):
                enemy.update_hitbox()

            if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                state.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

    def draw_enemy_player(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            if isinstance(enemy, TransportWorm):
                if self.map_scroll_speed_per_frame == 0:
                    enemy.draw(state.DISPLAY, self.camera)
                continue
            if isinstance(enemy, Slaver):
                if self.map_scroll_speed_per_frame == 0:
                    enemy.draw(state.DISPLAY, self.camera)
                continue
            enemy.draw(state.DISPLAY, self.camera)

    def load_enemy_into_list(self,state):
        state.enemies.clear()

        for obj in self.tiled_map.objects:
            if obj.name == "level_4_boss":
                enemy = BossLevelFour()
            elif obj.name == "transport_worm":
                enemy = TransportWorm()
            elif obj.name == "kamikazi_drone":
                enemy = KamikazeDrone()
            elif obj.name == "bile_spitter":
                enemy = BileSpitter()
            elif obj.name == "blade_spinner":
                enemy = BladeSpinner()
            elif obj.name == "fire_launcher":
                enemy = FireLauncher()
            elif obj.name == "tri_spitter":
                enemy = TriSpitter()
            elif obj.name == "slaver":
                enemy = Slaver()
            else:
                continue

            enemy.x = obj.x
            enemy.y = obj.y
            enemy.width = obj.width
            enemy.height = obj.height
            enemy.update_hitbox()
            enemy.camera = self.camera
            enemy.target_player = self.starship
            state.enemies.append(enemy)




