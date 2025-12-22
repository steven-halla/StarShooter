import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Monsters.AcidLauncher import AcidLauncher
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.Ravager import Ravager
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.SporeFlower import SporeFlower
from Entity.Monsters.TriSpitter import TriSpitter
from Entity.Monsters.WaspStinger import WaspStinger
from Entity.StarShip import StarShip
from Levels.LevelTwo import LevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelOne(VerticalBattleScreen):
    def __init__(self):
        super().__init__()
        # self.starship: StarShip = StarShip()

        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level1.tmx")
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
        # self.load_enemy_into_list()
        self.napalm_list: list = []
        self.total_enemies = 40
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
        super().update(state)
        if len(self.missed_enemies) > 9:
            print("GAME OVER!!!")
            self.game_over = True
        now = pygame.time.get_ticks()
        elapsed = now - self.level_start_time

        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        for enemy in list(self.bileSpitterGroup):

            # -------- MISS DETECTION --------
            if enemy.y > screen_bottom:
                if enemy not in self.missed_enemies:
                    self.missed_enemies.append(enemy)
                    print("enemy missed")
                continue  # stop processing this enemy

            enemy.update()

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
        if not self.bossLevelOneGroup and not self.level_complete:
            self.level_complete = True


        self.extract_object_names()
        if self.level_complete:

            next_level = LevelTwo()
            next_level.set_player(state.starship)
            state.currentScreen = next_level
            next_level.start(state)
            print(type(state.currentScreen).__name__)

            return

    def draw(self, state):
        super().draw(state)
        # ================================
        # ENEMY COUNTER (TOP OF SCREEN)
        # ================================
        font = pygame.font.Font(None, 28)

        current_enemies = (
                len(self.bileSpitterGroup)
                + len(self.triSpitterGroup)
                + len(self.bladeSpinnerGroup)
                + len(self.bossLevelOneGroup)
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

        enemy_text = font.render(
            f"Enemies {self.enemies_killed}/40",
            True,
            (255, 255, 255)
        )
        state.DISPLAY.blit(enemy_text, (10, 50))
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

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.draw(state.DISPLAY, self.camera)

        for blade in self.bladeSpinnerGroup:
            blade.draw(state.DISPLAY, self.camera)
        for boss in self.bossLevelOneGroup:
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
                list(self.bossLevelOneGroup)
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
        for obj in self.tiled_map.objects:
            # ⭐ LOAD ENEMIES (existing code)
            if obj.name == "level_1_boss":
                enemy = BossLevelOne()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.bossLevelOneGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship

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
        for boss in list(self.bossLevelOneGroup):

            if boss.y > screen_bottom:
                if boss not in self.missed_enemies:
                    self.missed_enemies.append(boss)
                    print("enemy missed")
                continue

            boss.update()

            if boss.enemyBullets:
                self.enemy_bullets.extend(boss.enemyBullets)
                boss.enemyBullets.clear()

            if boss.enemyHealth <= 0:
                self.bossLevelOneGroup.remove(boss)
                print("level complete")


        # -------------------------
        # BLADES
        # -------------------------
        for blade in list(self.bladeSpinnerGroup):

            if blade.y > screen_bottom:
                if blade not in self.missed_enemies:
                    self.missed_enemies.append(blade)
                    print("enemy missed")
                continue

            blade.update()

            if blade.enemyHealth <= 0:
                self.bladeSpinnerGroup.remove(blade)

        # -------------------------
        # BILE SPITTERS
        # -------------------------
        for enemy in list(self.bileSpitterGroup):

            if enemy.y > screen_bottom:
                if enemy not in self.missed_enemies:
                    self.missed_enemies.append(enemy)
                    print("enemy missed")
                continue

            enemy.update()

            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)
            else:
                enemy.color = GlobalConstants.RED

            enemy.update_hitbox()

            if enemy.enemyBullets:
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

        # -------------------------
        # TRI SPITTERS
        # -------------------------
        for enemy_tri_spitter in list(self.triSpitterGroup):

            if enemy_tri_spitter.y > screen_bottom:
                if enemy_tri_spitter not in self.missed_enemies:
                    self.missed_enemies.append(enemy_tri_spitter)
                    print("enemy missed")
                continue

            enemy_tri_spitter.update()

            if self.starship.hitbox.colliderect(enemy_tri_spitter.hitbox):
                enemy_tri_spitter.color = (135, 206, 235)
            else:
                enemy_tri_spitter.color = GlobalConstants.RED

            enemy_tri_spitter.update_hitbox()

            if enemy_tri_spitter.enemyBullets:
                self.enemy_bullets.extend(enemy_tri_spitter.enemyBullets)
                enemy_tri_spitter.enemyBullets.clear()
