import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelFour import BossLevelFour
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Monsters.AcidLauncher import AcidLauncher
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.Ravager import Ravager
from Entity.Monsters.Slaver import Slaver
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.SporeFlower import SporeFlower
from Entity.Monsters.TransportWorm import TransportWorm
from Entity.Monsters.TriSpitter import TriSpitter
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelFour(VerticalBattleScreen):
    def __init__(self):
        super().__init__()
        # self.starship: StarShip = StarShip()

        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level4.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400 # y position of map
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        self.camera_y = self.WORLD_HEIGHT - window_height # look at bottom of map
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = .4 # move speed of camera

        self.bileSpitterGroup: list[BileSpitter] = []
        self.kamikazeDroneGroup: list[KamikazeDrone] = []
        self.triSpitterGroup: list[TriSpitter] = []
        self.fireLauncherGroup: list[FireLauncher] = []
        self.bladeSpinnerGroup: list[BladeSpinner] = []
        self.transportWormGroup: list[TransportWorm] = []
        self.bossLevelFourGroup: list[BossLevelFour] = []
        # self.load_enemy_into_list()
        self.napalm_list: list = []
        self.total_enemies = 40
        self.creep_last_spawn_time = 0
        self.prev_enemy_count: int = None
        self.enemies_killed: int = 0

        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.missed_enemies = []
        self.game_over: bool = False
        self.level_complete = False

    def start(self, state) -> None:
        player_x = None
        player_y = None

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list()


    def update(self, state) -> None:
        # for boss in self.bossLevelFourGroup:
        #     print(f"[LEVEL 4 BOSS HP] {boss.enemyHealth}")
        BUFFER = -100  # pixels of grace


        worm_on_screen = False

        screen_top = self.camera.y - BUFFER
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom) + BUFFER

        for worm in self.transportWormGroup:
            if worm.y + worm.height >= screen_top and worm.y <= screen_bottom:
                worm_on_screen = True
                break

        # 🔒 FREEZE OR RESTORE SCROLL

        # screen bounds with padding (WORLD SPACE)
        # screen bounds with padding (WORLD SPACE)
        # --- FIXED VERSION USING THE CREEP LAYER (ONLY THIS BLOCK) ---

        # get creep layer safely (ONCE, before loop)
        try:
            creep_layer = self.tiled_map.get_layer_by_name("creep")
        except ValueError:
            creep_layer = None

        PADDING = 100
        screen_top = self.camera.y - PADDING
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom) + PADDING

        screen_left = self.camera.x
        screen_right = self.camera.x + (self.camera.window_width / self.camera.zoom)

        if worm_on_screen:
            self.map_scroll_speed_per_frame = 0
            now = pygame.time.get_ticks()

            # =====================================
            # CREEP DETECTION (GLOBAL, ONCE)
            # =====================================
            creep_found_on_screen = False

            if creep_layer is not None:
                tile_w = self.tiled_map.tilewidth
                tile_h = self.tiled_map.tileheight

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

            # =====================================
            # CREEP SPAWN (TOP OF SCREEN)
            # =====================================
            if creep_found_on_screen:
                # print("creep detected")

                if now - self.creep_last_spawn_time >= 3000:
                    slaver = Slaver()

                    slaver.x = self.camera.x
                    slaver.y = self.camera.y

                    slaver.camera = self.camera
                    slaver.target_player = self.starship

                    slaver.width = 16
                    slaver.height = 16
                    slaver.update_hitbox()

                    self.slaverGroup.append(slaver)
                    self.creep_last_spawn_time = now

            # =====================================
            # WORM SUMMONING (UNCHANGED)
            # =====================================
            for worm in self.transportWormGroup:

                # worm must be on screen
                if not (
                        worm.y + worm.height >= screen_top and
                        worm.y <= screen_bottom
                ):
                    continue

                # player must be on screen
                player = self.starship
                if not (
                        player.y + player.height >= screen_top and
                        player.y <= screen_bottom
                ):
                    continue

                if now - worm.last_summon_time >= worm.summon_interval_ms:
                    worm.summon_enemy(
                        enemy_classes=[
                            BileSpitter,
                            KamikazeDrone,
                            TriSpitter,
                            FireLauncher,
                        ],
                        enemy_groups={
                            BileSpitter: self.bileSpitterGroup,
                            KamikazeDrone: self.kamikazeDroneGroup,
                            TriSpitter: self.triSpitterGroup,
                            FireLauncher: self.fireLauncherGroup,
                        },
                        spawn_y_offset=20
                    )

                    for enemy in (
                            self.bileSpitterGroup +
                            self.kamikazeDroneGroup +
                            self.triSpitterGroup +
                            self.fireLauncherGroup
                    ):
                        enemy.width = 16
                        enemy.height = 16
                        enemy.update_hitbox()

                    worm.last_summon_time = now
        else:
            self.map_scroll_speed_per_frame = 0.4

        # try:
        #     creep_layer = self.tiled_map.get_layer_by_name("creep")
        # except ValueError:
        #     creep_layer = None
        #
        # PADDING = 100
        # screen_top = self.camera.y - PADDING
        # screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom) + PADDING
        #
        # if worm_on_screen:
        #     self.map_scroll_speed_per_frame = 0
        #     now = pygame.time.get_ticks()
        #
        #     for worm in self.transportWormGroup:
        #
        #         # worm must be on screen
        #         if not (
        #                 worm.y + worm.height >= screen_top and
        #                 worm.y <= screen_bottom
        #         ):
        #             continue
        #
        #         # creep layer must exist
        #         if creep_layer is None:
        #             continue
        #
        #         # --- CREEP TILE CHECK ---
        #         tile_x = int(worm.x // self.tiled_map.tilewidth)
        #         tile_y = int(worm.y // self.tiled_map.tileheight)
        #
        #         # bounds safety
        #         if tile_y < 0 or tile_y >= len(creep_layer.data):
        #             continue
        #         if tile_x < 0 or tile_x >= len(creep_layer.data[tile_y]):
        #             continue
        #
        #         tile = creep_layer.data[tile_y][tile_x]
        #         if tile is None:
        #             continue
        #
        #         # --- SUMMON ---
        #         if now - worm.last_summon_time >= worm.summon_interval_ms:
        #             worm.summon_enemy(
        #                 enemy_classes=[
        #                     BileSpitter,
        #                     KamikazeDrone,
        #                     TriSpitter,
        #                     FireLauncher,
        #                 ],
        #                 enemy_groups={
        #                     BileSpitter: self.bileSpitterGroup,
        #                     KamikazeDrone: self.kamikazeDroneGroup,
        #                     TriSpitter: self.triSpitterGroup,
        #                     FireLauncher: self.fireLauncherGroup,
        #                 },
        #                 spawn_y_offset=20
        #             )
        #
        #             # HARD SIZE ENFORCEMENT
        #             for enemy in (
        #                     self.bileSpitterGroup +
        #                     self.kamikazeDroneGroup +
        #                     self.triSpitterGroup +
        #                     self.fireLauncherGroup
        #             ):
        #                 enemy.width = 16
        #                 enemy.height = 16
        #                 enemy.update_hitbox()
        #
        #             worm.last_summon_time = now
        # else:
        #     self.map_scroll_speed_per_frame = 0.4
        # # PADDING = 100
        # screen_top = self.camera.y - PADDING
        # screen_bottom = self.camera.y + (self.window_height / self.camera.zoom) + PADDING
        #
        # if worm_on_screen:
        #     self.map_scroll_speed_per_frame = 0
        #     now = pygame.time.get_ticks()
        #
        #     for worm in self.transportWormGroup:
        #
        #         # ✅ ONLY WORMS ACTUALLY ON SCREEN CAN SUMMON
        #         if not (
        #                 worm.y + worm.height >= screen_top and
        #                 worm.y <= screen_bottom
        #         ):
        #             continue
        #
        #         if now - worm.last_summon_time >= worm.summon_interval_ms:
        #             worm.summon_enemy(
        #                 enemy_classes=[
        #                     BileSpitter,
        #                     KamikazeDrone,
        #                     TriSpitter,
        #                     FireLauncher,
        #                 ],
        #                 enemy_groups={
        #                     BileSpitter: self.bileSpitterGroup,
        #                     KamikazeDrone: self.kamikazeDroneGroup,
        #                     TriSpitter: self.triSpitterGroup,
        #                     FireLauncher: self.fireLauncherGroup,
        #                 },
        #                 spawn_y_offset=20
        #             )
        #
        #             # 🔒 HARD SIZE ENFORCEMENT (LEVEL 4 FIX)
        #             for enemy in (
        #                     self.bileSpitterGroup +
        #                     self.kamikazeDroneGroup +
        #                     self.triSpitterGroup +
        #                     self.fireLauncherGroup
        #             ):
        #                 enemy.width = 16
        #                 enemy.height = 16
        #                 enemy.update_hitbox()
        #
        #             worm.last_summon_time = now
        # else:
        #     self.map_scroll_speed_per_frame = 0.4
        super().update(state)
        # print("=== ENEMY LIST ===")
        # print(f"BileSpitter: {len(self.bileSpitterGroup)}")
        # print(f"TriSpitter: {len(self.triSpitterGroup)}")
        # print(f"BladeSpinner: {len(self.bladeSpinnerGroup)}")
        # print(f"firelauncher: {len(self.fireLauncherGroup)}")
        # print(f"transportworm: {len(self.transportWormGroup)}")
        # print(f"kamikazedrone: {len(self.kamikazeDroneGroup)}")
        # print(f"BossLevelFour: {len(self.bossLevelFourGroup)}")
        # print(
        #     f"TOTAL: "
        #     f"{len(self.bileSpitterGroup) + len(self.triSpitterGroup) + len(self.bladeSpinnerGroup) + len(self.bossLevelFourGroup)}"
        # )
        # print("==================")
        # for worm in list(self.transportWormGroup):
        #         #     worm.update()
        #         #     print(f"[TransportWorm HP] {worm.enemyHealth}")
        #         #
        #         #     if worm.enemyHealth <= 0:
        #         #         self.transportWormGroup.remove(worm)


        now = pygame.time.get_ticks()
        elapsed = now - self.level_start_time

        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        # for enemy in list(self.bileSpitterGroup):
        #
        #     # -------- MISS DETECTION --------
        #     if enemy.y > screen_bottom:
        #         if enemy not in self.missed_enemies:
        #             self.missed_enemies.append(enemy)
        #             print("enemy missed")
        #         continue  # stop processing this enemy
        #
        #     enemy.update()

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
        # if not self.bossLevelFourGroup and not self.level_complete:
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

    def draw(self, state):
        super().draw(state)
        # ================================
        # ENEMY COUNTER (TOP OF SCREEN)
        # ================================
        font = pygame.font.Font(None, 28)

        current_enemies = (
                len(self.bileSpitterGroup)
                + len(self.triSpitterGroup)
                +len(self.slaverGroup)
                + len(self.bladeSpinnerGroup)
                + len(self.bossLevelFourGroup)
                + len(self.kamikazeDroneGroup)
                + len(self.fireLauncherGroup)
                + len(self.transportWormGroup)

        )
        # print(current_enemies)
        # initialize on first frame
        if self.prev_enemy_count is None:
            self.prev_enemy_count = current_enemies
        else:
            # if enemies decreased, count the difference
            if current_enemies < self.prev_enemy_count:
                self.enemies_killed += (self.prev_enemy_count - current_enemies)

            self.prev_enemy_count = current_enemies

        # enemy_text = font.render(
        #     f"Enemies {self.enemies_killed}/40",
        #     True,
        #     (255, 255, 255)
        # )
        # state.DISPLAY.blit(enemy_text, (10, 50))
        for napalm in self.napalm_list:
            napalm.draw(state.DISPLAY, self.camera)
        zoom = self.camera.zoom

        for obj in self.tiled_map.objects:
            if hasattr(obj, "image") and obj.image is not None:
                screen_x = self.camera.world_to_screen_x(obj.x)
                screen_y = self.camera.world_to_screen_y(obj.y)
                state.DISPLAY.blit(obj.image, (screen_x, screen_y))

        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)

        for enemy in self.bileSpitterGroup:
            enemy.draw(state.DISPLAY, self.camera)


        for enemy in self.kamikazeDroneGroup:
            enemy.draw(state.DISPLAY, self.camera)


        for enemy in self.slaverGroup:
            enemy.draw(state.DISPLAY, self.camera)


        for enemy in self.fireLauncherGroup:
            enemy.draw(state.DISPLAY, self.camera)

        for enemy in self.transportWormGroup:
            enemy.draw(state.DISPLAY, self.camera)

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.draw(state.DISPLAY, self.camera)

        for blade in self.bladeSpinnerGroup:
            blade.draw(state.DISPLAY, self.camera)
        for boss in self.bossLevelFourGroup:
            boss.draw(state.DISPLAY, self.camera)

        for enemy_tri_spitter in self.triSpitterGroup:
            hb = pygame.Rect(
                self.camera.world_to_screen_x(enemy_tri_spitter.hitbox.x),
                self.camera.world_to_screen_y(enemy_tri_spitter.hitbox.y),
                int(enemy_tri_spitter.hitbox.width * zoom),
                int(enemy_tri_spitter.hitbox.height * zoom)
            )
            pygame.draw.rect(state.DISPLAY, (255, 255, 0), hb, 2)

        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        enemies = (
                list(self.bileSpitterGroup) +
                list(self.triSpitterGroup) +
                list(self.bladeSpinnerGroup) +
                list(self.bossLevelFourGroup) +
                list(self.slaverGroup) +
                list(self.kamikazeDroneGroup) +
                list(self.fireLauncherGroup) +
                list(self.transportWormGroup)
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

    def load_enemy_into_list(self):
        self.bileSpitterGroup.clear()
        self.triSpitterGroup.clear()
        self.bladeSpinnerGroup.clear()
        self.fireLauncherGroup.clear()
        self.kamikazeDroneGroup.clear()
        self.transportWormGroup.clear()
        self.bossLevelFourGroup.clear()
        for obj in self.tiled_map.objects:
            # ⭐ LOAD ENEMIES (existing code)
            if obj.name == "level_4_boss":
                enemy = BossLevelFour()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.bossLevelFourGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
                continue
            if obj.name == "transport_worm":
                drone = TransportWorm()
                drone.x = obj.x
                drone.y = obj.y
                drone.width = obj.width
                drone.height = obj.height
                drone.update_hitbox()
                self.transportWormGroup.append(drone)
                drone.camera = self.camera
                drone.target_player = self.starship

                continue

            if obj.name == "kamikazi_drone":
                drone = KamikazeDrone()
                drone.x = obj.x
                drone.y = obj.y
                drone.width = obj.width
                drone.height = obj.height
                drone.update_hitbox()
                self.kamikazeDroneGroup.append(drone)
                drone.camera = self.camera
                drone.target_player = self.starship

                continue
            if obj.name == "bile_spitter":
                enemy = BileSpitter()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                enemy.target_player = self.starship
                self.bileSpitterGroup.append(enemy)

            if obj.name == "blade_spinner":
                enemy = BladeSpinner()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                self.bladeSpinnerGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
                continue

            if obj.name == "fire_launcher":
                enemy = FireLauncher()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.fireLauncherGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship

            if obj.name == "tri_spitter":
                enemy_tri_spitter = TriSpitter()
                enemy_tri_spitter.x = obj.x
                enemy_tri_spitter.y = obj.y
                enemy_tri_spitter.width = obj.width
                enemy_tri_spitter.height = obj.height
                enemy_tri_spitter.update_hitbox()
                self.triSpitterGroup.append(enemy_tri_spitter)
                enemy_tri_spitter.camera = self.camera
                enemy_tri_spitter.target_player = self.starship
                continue
            if obj.name == "slaver":
                slaver = Slaver()
                slaver.x = obj.x
                slaver.y = obj.y
                slaver.width = obj.width
                slaver.height = obj.height
                slaver.update_hitbox()
                self.slaverGroup.append(slaver)
                slaver.camera = self.camera
                slaver.target_player = self.starship
                continue

    def enemy_helper(self):
        # screen bottom in WORLD coordinates
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)



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
        # -------------------------
        # BOSS
        # -------------------------
        for boss in list(self.bossLevelFourGroup):

            # ✅ REQUIRED — DO NOT REMOVE
            boss.update()

            # -------------------------
            # PLAYER BULLETS → BOSS ONLY
            # -------------------------
            for bullet in list(self.player_bullets):
                bullet_rect = pygame.Rect(
                    bullet.x,
                    bullet.y,
                    bullet.width,
                    bullet.height
                )

                if bullet_rect.colliderect(boss.hitbox):

                    # ROUTE DAMAGE THROUGH BOSS LOGIC
                    if hasattr(boss, "take_damage"):
                        boss.take_damage(bullet.damage)
                    else:
                        boss.enemyHealth -= bullet.damage

                    print(
                        f"[BOSS HIT] "
                        f"ShieldActive={boss.shield_active} "
                        f"ShieldHP={getattr(boss, 'shield_hp', 'N/A')} "
                        f"BossHP={boss.enemyHealth}"
                    )

                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)

                    break  # one bullet per frame per boss

            # -------------------------
            # BOSS BULLETS
            # -------------------------
            if boss.enemyBullets:
                self.enemy_bullets.extend(boss.enemyBullets)
                boss.enemyBullets.clear()

            # -------------------------
            # BOSS DEATH
            # -------------------------
            if boss.enemyHealth <= 0:
                self.bossLevelFourGroup.remove(boss)
                print("level complete")
        # for boss in list(self.bossLevelFourGroup):
        #
        #     boss.update()
        #
        #     if boss.enemyBullets:
        #         self.enemy_bullets.extend(boss.enemyBullets)
        #         boss.enemyBullets.clear()
        #
        #     if boss.enemyHealth <= 0:
        #         self.bossLevelFourGroup.remove(boss)
        #         print("level complete")

        for blade in list(self.bladeSpinnerGroup):
            blade.update()
            if blade.enemyHealth <= 0:
                self.bladeSpinnerGroup.remove(blade)

        for fire in list(self.fireLauncherGroup):
            fire.update()

            if fire.enemyBullets:
                self.enemy_bullets.extend(fire.enemyBullets)
                fire.enemyBullets.clear()

            if fire.enemyHealth <= 0:
                self.fireLauncherGroup.remove(fire)

        for enemy in self.bileSpitterGroup:
            enemy.update()
            enemy.update_hitbox()

            if enemy.enemyBullets:
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

        for enemy in self.slaverGroup:
            enemy.update()
            enemy.update_hitbox()

            if enemy.enemyBullets:
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

        for drone in list(self.kamikazeDroneGroup):
            drone.update()

            if drone.enemyHealth <= 0:
                self.kamikazeDroneGroup.remove(drone)

        for worm in list(self.transportWormGroup):
            worm.update()

            if worm.enemyHealth <= 0:
                self.transportWormGroup.remove(worm)

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.update()
            enemy_tri_spitter.update_hitbox()

            if enemy_tri_spitter.enemyBullets:
                self.enemy_bullets.extend(enemy_tri_spitter.enemyBullets)
                enemy_tri_spitter.enemyBullets.clear()

