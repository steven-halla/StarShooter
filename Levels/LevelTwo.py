import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Bosses.BossLevelTwo import BossLevelTwo
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
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelTwo(VerticalBattleScreen):
    def __init__(self):
        super().__init__()
        # self.starship: StarShip = StarShip()

        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level2.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400  # y position of map

        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        self.camera_y = self.WORLD_HEIGHT - window_height  # look at bottom of map
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)

        self.map_scroll_speed_per_frame: float = .4  # move speed of camera

        self.bileSpitterGroup: list[BileSpitter] = []
        self.kamikazeDroneGroup: list[KamikazeDrone] = []
        self.triSpitterGroup: list[TriSpitter] = []
        self.bossLevelTwoGroup: list[BossLevelTwo] = []

        self.napalm_list: list = []

        self.total_enemies = 40
        self.prev_enemy_count: int = None
        self.enemies_killed: int = 0

        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False

        # --------------------------------
        # SIDE RECT (ONLY HP SYSTEM)
        # --------------------------------
        self.side_rect_width = 16
        self.side_rect_height = 16
        self.side_rect_hp = 50
        self.side_rect_max_hp = 50

        self.side_rect_hitbox = pygame.Rect(0, 0, 0, 0)

        self.game_over: bool = False

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
        print(self.side_rect_hp)

        # UPDATE INVINCIBILITY TIMER FIRST
        self.update_side_rect_invincibility()

        print("SIDE RECT HP:", self.side_rect_hp, "INVINCIBLE:", self.side_rect_invincible)

        # -------------------------
        # UPDATE SIDE RECT HITBOX (WORLD SPACE)
        # -------------------------
        side_x = self.starship.x + self.starship.width + 10
        side_y = self.starship.y + (self.starship.height // 2) - (self.side_rect_height // 2)

        self.side_rect_hitbox.update(
            int(side_x),
            int(side_y),
            self.side_rect_width,
            self.side_rect_height
        )

        # -------------------------
        # HAZARD → SIDE RECT (WITH INVINCIBILITY GATE)
        # -------------------------
        hazard_layer = self.tiled_map.get_layer_by_name("hazard")

        if self.side_rect_hp > 0 and not self.side_rect_invincible:
            for x, y, gid in hazard_layer:
                if gid == 0:
                    continue

                tile_rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )

                if self.side_rect_hitbox.colliderect(tile_rect):
                    self.side_rect_hp -= 1
                    self.side_rect_invincible = True
                    self.side_rect_invincible_start_time = pygame.time.get_ticks()
                    print("⚠️ Side rect took hazard damage:", self.side_rect_hp)
                    break

        self.enemy_helper()

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

        for enemy in self.bileSpitterGroup:
            enemy.draw(state.DISPLAY, self.camera)
        for enemy in self.fireLauncherGroup:
            enemy.draw(state.DISPLAY, self.camera)
        for boss in self.bossLevelTwoGroup:
            boss.draw(state.DISPLAY, self.camera)

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.draw(state.DISPLAY, self.camera)

        for blade in self.bladeSpinnerGroup:
            blade.draw(state.DISPLAY, self.camera)

        for boss in self.bossLevelTwoGroup:
            boss.draw(state.DISPLAY, self.camera)

        # -------------------------
        # SIDE RECT HP BAR (ONLY HP BAR)
        # -------------------------
        side_screen_x = self.camera.world_to_screen_x(self.side_rect_hitbox.x)
        side_screen_y = self.camera.world_to_screen_y(self.side_rect_hitbox.y)

        side_w = int(self.side_rect_hitbox.width * zoom)
        side_h = int(self.side_rect_hitbox.height * zoom)

        hp_ratio = max(0, self.side_rect_hp / self.side_rect_max_hp)
        hp_width = int(side_w * hp_ratio)

        # background
        pygame.draw.rect(
            state.DISPLAY,
            (60, 60, 60),
            (side_screen_x, side_screen_y, side_w, side_h)
        )

        # HP fill
        pygame.draw.rect(
            state.DISPLAY,
            (0, 255, 0),
            (side_screen_x, side_screen_y, hp_width, side_h)
        )

        # outline
        pygame.draw.rect(
            state.DISPLAY,
            (255, 255, 255),
            (side_screen_x, side_screen_y, side_w, side_h),
            1
        )

        pygame.display.flip()
    def get_nearest_enemy(self, missile):
        enemies = (
                list(self.bileSpitterGroup) +
                list(self.triSpitterGroup) +
                list(self.bladeSpinnerGroup) +
                list(self.fireLauncherGroup) +
                list(self.bossLevelTwoGroup)
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
            if obj.name == "level_2_boss":
                enemy = BossLevelTwo()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.bossLevelTwoGroup.append(enemy)
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

    def enemy_helper(self):
        now = pygame.time.get_ticks()

        # --------------------------------
        # INIT SIDE RECT INVULNERABILITY
        # --------------------------------
        if not hasattr(self, "side_rect_invincible"):
            self.side_rect_invincible = False
            self.side_rect_invincible_start_time = 0

        # --------------------------------
        # SIDE RECT INVULNERABILITY TIMER
        # --------------------------------
        if self.side_rect_invincible:
            if now - self.side_rect_invincible_start_time >= 1000:
                self.side_rect_invincible = False

        # --------------------------------
        # NAPALM UPDATE (PLAYER ONLY)
        # --------------------------------
        for napalm in list(self.napalm_list):
            napalm.update()

            if napalm.is_active and napalm.hits(self.starship.hitbox):
                if not self.starship.invincible:
                    self.starship.shipHealth -= napalm.damage
                    self.starship.on_hit()

            if not napalm.is_active:
                self.napalm_list.remove(napalm)

        # --------------------------------
        # ENEMY BULLETS → SIDE RECT (NEW)
        # --------------------------------
        for bullet in list(self.enemy_bullets):

            # bullet rect in WORLD space
            bullet_rect = pygame.Rect(
                bullet.x,
                bullet.y,
                bullet.width,
                bullet.height
            )

            # SIDE RECT TAKES PRIORITY
            if bullet_rect.colliderect(self.side_rect_hitbox):

                if not self.side_rect_invincible:
                    self.side_rect_hp -= bullet.damage
                    self.side_rect_invincible = True
                    self.side_rect_invincible_start_time = now
                    print("⚠️ SIDE RECT HIT:", self.side_rect_hp)

                # bullet is ALWAYS destroyed
                self.enemy_bullets.remove(bullet)
                continue

        # --------------------------------
        # METAL SHIELD → ENEMY BULLETS
        # --------------------------------
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

        # --------------------------------
        # ENEMY UPDATES + BULLET SPAWNING
        # --------------------------------
        for boss in list(self.bossLevelTwoGroup):
            boss.update()

            if boss.enemyBullets:
                self.enemy_bullets.extend(boss.enemyBullets)
                boss.enemyBullets.clear()

            if boss.enemyHealth <= 0:
                self.bossLevelTwoGroup.remove(boss)

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

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.update()
            enemy_tri_spitter.update_hitbox()

            if enemy_tri_spitter.enemyBullets:
                self.enemy_bullets.extend(enemy_tri_spitter.enemyBullets)
                enemy_tri_spitter.enemyBullets.clear()

    # SIDE RECT INVINCIBILITY TIMER (NO DAMAGE LOGIC HERE)
    # =========================
    def update_side_rect_invincibility(self) -> None:
        if not hasattr(self, "side_rect_invincible"):
            self.side_rect_invincible = False
            self.side_rect_invincible_start_time = 0
            return

        if self.side_rect_invincible:
            if pygame.time.get_ticks() - self.side_rect_invincible_start_time >= 1000:
                self.side_rect_invincible = False
