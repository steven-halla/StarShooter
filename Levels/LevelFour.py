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
    def __init__(self,textbox):
        super().__init__(textbox)
        # self.starship: StarShip = StarShip()

        self.level_start = True
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
        self.worms_saved: list = []
        self.touched_worms: list[TransportWorm] = []


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
        # self.load_enemy_into_list()


    def update(self, state) -> None:
        super().update(state)

        if self.level_start == True:
            self.level_start = False
            self.starship.shipHealth = 222
            self.save_state.capture_player(self.starship, self.__class__.__name__)
            self.save_state.save_to_file("player_save.json")

        # for boss in self.bossLevelFourGroup:
        #     print(f"[LEVEL 4 BOSS HP] {boss.enemyHealth}")
        BUFFER = -100  # pixels of grace


        worm_on_screen = False

        screen_top = self.camera.y - BUFFER
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom) + BUFFER

        worm_on_screen = False
        worm = "transport_worm"

        for enemy in self.enemies:
            if getattr(enemy, "enemy_name", None) != worm:
                continue

            if enemy.y + enemy.height >= screen_top and enemy.y <= screen_bottom:
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

                if now - self.creep_last_spawn_time >= 5500:
                    slaver = Slaver()

                    slaver.x = self.camera.x
                    slaver.y = self.camera.y

                    slaver.camera = self.camera
                    slaver.target_player = self.starship

                    slaver.width = 16
                    slaver.height = 16
                    slaver.update_hitbox()

                    slaver.transport_worms = self.transportWormGroup
                    slaver.target_worm = worm

                    # 🔑 ADD THIS LINE
                    slaver.touched_worms = self.touched_worms

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

        if self.touched_worms:
            print(
                "[LEVEL 4 READ] touched_worms =",
                [(w.enemyHealth, w.x, w.y) for w in self.touched_worms]
            )

            if len(self.touched_worms) > 0:
                print("you lost")



        now = pygame.time.get_ticks()
        elapsed = now - self.level_start_time

        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        # for enemy in list(self.bileSpitterGroup):
        #

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
                # self.player_missiles.append(missile)

                # if missile.target_enemy is not None:
                #     print(f"Missile locked onto: {type(missile.target_enemy).__name__} "
                #           f"at ({missile.target_enemy.x}, {missile.target_enemy.y})")
                # else:
                #     print("Missile locked onto: NONE (no enemies found)")
        # self.enemy_helper()
        # if not self.bossLevelFourGroup and not self.level_complete:
        #     self.level_complete = True


        # self.extract_object_names()
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

        for enemy in self.enemies:
            enemy.draw(state.DISPLAY, self.camera)

            # optional hitbox debug for tri_spitter only
            if getattr(enemy, "enemy_name", None) == "tri_spitter":
                hb = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.hitbox.x),
                    self.camera.world_to_screen_y(enemy.hitbox.y),
                    int(enemy.hitbox.width * zoom),
                    int(enemy.hitbox.height * zoom)
                )
                pygame.draw.rect(state.DISPLAY, (255, 255, 0), hb, 2)

        self.draw_ui_panel(state.DISPLAY)

        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        enemies = self.enemies

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
        self.enemies.clear()

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

            self.enemies.append(enemy)
            # print(self.enemies)


    def enemy_helper(self):
        # screen bottom in WORLD coordinates
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        boss = "level_4_boss"

        # -------------------------
        # METAL SHIELD → ENEMY BULLETS
        # -------------------------
        for shield in list(self.player_bullets):

            if shield.weapon_name != "Metal Shield":
                continue

            if not shield.is_active:
                self.player_bullets.remove(shield)
                continue

            shield_rect = pygame.Rect(
                shield.x,
                shield.y,
                shield.width,
                shield.height
            )

            for bullet in list(self.enemy_bullets):
                if bullet.collide_with_rect(shield_rect):

                    absorbed = shield.absorb_hit()

                    if bullet in self.enemy_bullets:
                        self.enemy_bullets.remove(bullet)

                    if absorbed and shield in self.player_bullets:
                        self.player_bullets.remove(shield)

                    break

                for enemy in list(self.enemies):
                    if getattr(enemy, "enemy_name", None) != boss:
                        continue

                    # ✅ REQUIRED — DO NOT REMOVE
                    enemy.update()

                    # -------------------------
                    # PLAYER BULLETS → BOSS ONLY
                    # -------------------------
                    # for bullet in list(self.player_bullets):
                    #     bullet_rect = pygame.Rect(
                    #         bullet.x,
                    #         bullet.y,
                    #         bullet.width,
                    #         bullet.height
                    #     )
                    #
                    #     if bullet_rect.colliderect(enemy.hitbox):
                    #
                    #         # ROUTE DAMAGE THROUGH BOSS LOGIC
                    #         if hasattr(enemy, "take_damage"):
                    #             enemy.take_damage(bullet.damage)
                    #         else:
                    #             enemy.enemyHealth -= bullet.damage
                    #
                    #         print(
                    #             f"[BOSS HIT] "
                    #             f"ShieldActive={enemy.shield_active} "
                    #             f"ShieldHP={getattr(enemy, 'shield_hp', 'N/A')} "
                    #             f"BossHP={enemy.enemyHealth}"
                    #         )
                    #
                    #         if bullet in self.player_bullets:
                    #             self.player_bullets.remove(bullet)
                    #
                    #         break

            # -------------------------
            # BOSS BULLETS
            # -------------------------

            for enemy in list(self.enemies):
                if getattr(enemy, "enemy_name", None) != boss:
                    continue

                if enemy.enemyBullets:
                    self.enemy_bullets.extend(enemy.enemyBullets)
                    enemy.enemyBullets.clear()

                # -------------------------
                # BOSS DEATH
                # -------------------------
                if enemy.enemyHealth <= 0:
                    self.enemies.remove(enemy)
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

        for enemy in list(self.enemies):

            enemy_type = getattr(enemy, "enemy_name", None)

            # -------------------------
            # UPDATE
            # -------------------------
            enemy.update()

            if hasattr(enemy, "update_hitbox"):
                enemy.update_hitbox()

            # -------------------------
            # ENEMY BULLETS
            # -------------------------
            if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            # -------------------------
            # TYPE-SPECIFIC DEBUG / LOGIC
            # -------------------------
            if enemy_type == "transport_worm":
                print(
                    "[LEVEL 4] Touched worms:",
                    [(w.enemyHealth, w.x, w.y) for w in self.touched_worms]
                )

            if enemy_type == "slaver" and enemy.enemyHealth <= 0:
                print("[LEVEL 4] Slaver removed after touching worm")

            # -------------------------
            # DEATH
            # -------------------------
            if enemy.enemyHealth <= 0:
                self.enemies.remove(enemy)
