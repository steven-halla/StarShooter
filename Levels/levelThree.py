import random
from typing import Optional

import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Bosses.BossLevelThree import BossLevelThree
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
from Entity.SpaceStation import SpaceStation
from Entity.StarShip import StarShip
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelThree(VerticalBattleScreen):
    def __init__(self):
        super().__init__()
        # self.starship: StarShip = StarShip()

        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level3.tmx")
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
        self.fireLauncherGroup: list[FireLauncher] = []
        self.bladeSpinnerGroup: list[BladeSpinner] = []
        self.bossLevelThreeGroup: list[BossLevelThree] = []

        self.napalm_list: list = []
        self.space_station: Optional[SpaceStation] = None

        self.total_enemies = 40
        self.prev_enemy_count: int = None
        self.enemies_killed: int = 0

        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.enemy_wave_interval_ms = 180000
        self.last_enemy_wave_time = pygame.time.get_ticks()
        self.intial_wave: bool = True

        # --------------------------------
        # SIDE RECT (ONLY HP SYSTEM)
        # --------------------------------
        self.side_rect_width = 16
        self.side_rect_height = 16
        self.side_rect_hp = 50
        self.side_rect_max_hp = 50

        self.side_rect_hitbox = pygame.Rect(0, 0, 0, 0)

        self.game_over: bool = False
        # Level 3: disable base enemy bullet damage
        self.disable_player_bullet_damage = True

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

    def move_map_y_axis(self):
        pass

    def update(self, state) -> None:
        # Disable bullet damage
        self.starship.hitbox = pygame.Rect(0, 0, 0, 0)

        super().update(state)

        # 🔑 ALWAYS update melee hitbox AFTER movement
        self.starship.melee_hitbox = pygame.Rect(
            int(self.starship.x),
            int(self.starship.y),
            self.starship.width,
            self.starship.height
        )

        # Guard hitbox (bullets only)
        self.deflect_hitbox = pygame.Rect(
            int(self.starship.x - 0.5),
            int(self.starship.y - 0.5),
            17,
            17
        )

        # 🔥 MELEE DAMAGE CHECK (THIS WAS MISSING)
        for boss in self.bossLevelThreeGroup:
            boss.check_arm_damage(self.starship)

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
        for boss in self.bossLevelThreeGroup:
            boss.draw(state.DISPLAY, self.camera)

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.draw(state.DISPLAY, self.camera)

        for blade in self.bladeSpinnerGroup:
            blade.draw(state.DISPLAY, self.camera)
        for drone in self.kamikazeDroneGroup:
            drone.draw(state.DISPLAY, self.camera)

        for boss in self.bossLevelTwoGroup:
            boss.draw(state.DISPLAY, self.camera)

        if self.space_station is not None:
            self.space_station.draw(state.DISPLAY, self.camera)


        pygame.display.flip()
    def get_nearest_enemy(self, missile):

        enemies = (
                list(self.bileSpitterGroup) +
                list(self.triSpitterGroup) +
                list(self.bladeSpinnerGroup) +
                list(self.fireLauncherGroup) +
                list(self.kamikazeDroneGroup) +
                list(self.bossLevelThreeGroup)
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
            if obj.name == "space_station":
                self.space_station = SpaceStation(
                    x=obj.x,
                    y=obj.y,
                    width=obj.width,
                    height=obj.height,
                    max_hp=300
                )
            # ⭐ LOAD ENEMIES (existing code)
            if obj.name == "level_3_boss":
                enemy = BossLevelThree()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.bossLevelThreeGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship

            if obj.name == "kamikazi_drone":
                drone = KamikazeDrone()
                drone.x = obj.x
                drone.y = obj.y
                drone.width = obj.width
                drone.height = obj.height
                drone.update_hitbox()
                self.kamikazeDroneGroup.append(drone)
                drone.camera = self.camera

                # 🔑 TARGET SPACE STATION INSTEAD OF PLAYER
                drone.target_player = self.space_station

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

    def enemy_helper(self):
        now = pygame.time.get_ticks()
        print(self.starship.shipHealth)
        # print(
        #     f"BileSpitter: {len(self.bileSpitterGroup)} | "
        #     f"TriSpitter: {len(self.triSpitterGroup)} | "
        #     f"BladeSpinner: {len(self.bladeSpinnerGroup)} | "
        #     f"FireLauncher: {len(self.fireLauncherGroup)} | "
        #     f"KamikazeDrone: {len(self.kamikazeDroneGroup)} | "
        #     f"BossLevelThree: {len(self.bossLevelThreeGroup)}"
        # )

        if now - self.last_enemy_wave_time >= self.enemy_wave_interval_ms:
            self.spawn_enemy_wave()
            self.last_enemy_wave_time = now

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
        # DEFLECT + REFLECT LOGIC (BULLETS ONLY)
        # --------------------------------
        for bullet in list(self.enemy_bullets):

            bullet_rect = pygame.Rect(
                bullet.x,
                bullet.y,
                bullet.width,
                bullet.height
            )

            # ✅ FIXED DEFLECT LOGIC
            if bullet_rect.colliderect(self.deflect_hitbox):

                # --------------------------------
                # FORCE REFLECT (EVEN NO ENEMIES)
                # --------------------------------
                if not hasattr(bullet, "is_reflected"):
                    target = self.get_nearest_enemy(bullet)

                    # 🔑 NO ENEMY → FORCE DOWN
                    if target is None:
                        bullet.dx = 0
                        bullet.speed = -abs(bullet.speed) * 6  # 🔺 FORCE UP
                        bullet.is_reflected = True
                        bullet.damage = 0
                    else:
                        self.reflect_bullet(bullet)

                continue

            # --------------------------------
            # REFLECTED BULLETS → ENEMIES
            # --------------------------------
            if hasattr(bullet, "is_reflected"):

                enemies = (
                        list(self.bileSpitterGroup) +
                        list(self.triSpitterGroup) +
                        list(self.bladeSpinnerGroup) +
                        list(self.fireLauncherGroup) +
                        list(self.kamikazeDroneGroup) +
                        list(self.bossLevelThreeGroup)
                )

                for enemy in enemies:
                    enemy_rect = pygame.Rect(
                        enemy.x,
                        enemy.y,
                        enemy.width,
                        enemy.height
                    )

                    if bullet_rect.colliderect(enemy_rect):
                        enemy.enemyHealth -= bullet.damage

                        if bullet in self.enemy_bullets:
                            self.enemy_bullets.remove(bullet)

                        if enemy.enemyHealth <= 0:
                            if enemy in self.bileSpitterGroup:
                                self.bileSpitterGroup.remove(enemy)
                            elif enemy in self.triSpitterGroup:
                                self.triSpitterGroup.remove(enemy)
                            elif enemy in self.bladeSpinnerGroup:
                                self.bladeSpinnerGroup.remove(enemy)
                            elif enemy in self.fireLauncherGroup:
                                self.fireLauncherGroup.remove(enemy)
                            elif enemy in self.kamikazeDroneGroup:
                                self.kamikazeDroneGroup.remove(enemy)
                            elif enemy in self.bossLevelThreeGroup:
                                self.bossLevelThreeGroup.remove(enemy)

                        break

            # --------------------------------
            # SPACE STATION DAMAGE
            # --------------------------------
            if self.space_station is not None:
                if bullet_rect.colliderect(self.space_station.hitbox):
                    self.space_station.hp -= bullet.damage
                    if bullet in self.enemy_bullets:
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
        for boss in list(self.bossLevelThreeGroup):
            boss.update()

            if boss.enemyBullets:
                self.enemy_bullets.extend(boss.enemyBullets)
                boss.enemyBullets.clear()

            if boss.enemyHealth <= 0:
                self.bossLevelThreeGroup.remove(boss)

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

        for drone in list(self.kamikazeDroneGroup):
            drone.update()
            if drone.enemyHealth <= 0:
                self.kamikazeDroneGroup.remove(drone)

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.update()
            enemy_tri_spitter.update_hitbox()

            if enemy_tri_spitter.enemyBullets:
                self.enemy_bullets.extend(enemy_tri_spitter.enemyBullets)
                enemy_tri_spitter.enemyBullets.clear()

        # --------------------------------
        # ENEMY BODY COLLISION DAMAGE (LEVEL 3)
        # --------------------------------
        if not self.starship.invincible:
            player_rect = self.starship.melee_hitbox  # ← USE MELEE HITBOX

            enemies = (
                    list(self.bileSpitterGroup) +
                    list(self.triSpitterGroup) +
                    list(self.bladeSpinnerGroup) +
                    list(self.fireLauncherGroup) +
                    list(self.kamikazeDroneGroup) +
                    list(self.bossLevelThreeGroup)
            )

            for enemy in enemies:
                enemy_rect = pygame.Rect(
                    enemy.x,
                    enemy.y,
                    enemy.width,
                    enemy.height
                )

                if player_rect.colliderect(enemy_rect):

                    # 🔥 KAMIKAZE DRONE SPECIAL CASE
                    if enemy in self.kamikazeDroneGroup:
                        self.starship.shipHealth -= 20
                        self.starship.on_hit()
                        self.kamikazeDroneGroup.remove(enemy)
                    else:
                        self.starship.shipHealth -= 10
                        self.starship.on_hit()

                    break  # one hit per frame

    def reflect_bullet(self, bullet):
        target = self.get_nearest_enemy(bullet)

        # --------------------------------
        # 🔑 FALLBACK: NO ENEMIES ON SCREEN
        # --------------------------------
        if target is None:
            bullet.dx = 0
            bullet.speed = abs(bullet.speed) * 6  # force DOWN
            bullet.is_reflected = True
            bullet.damage = 0  # reflected but harmless
            return

        # Bullet center
        bx = bullet.x + bullet.width / 2
        by = bullet.y + bullet.height / 2

        # Enemy center
        ex = target.x + target.width / 2
        ey = target.y + target.height / 2

        dx = ex - bx
        dy = ey - by
        dist = (dx * dx + dy * dy) ** 0.5
        if dist == 0:
            return

        dx /= dist
        dy /= dist

        reflect_speed = abs(bullet.speed) if bullet.speed != 0 else 4

        bullet.dx = dx * reflect_speed * 6
        bullet.speed = dy * reflect_speed * 6
        bullet.is_reflected = True
        bullet.damage = 100
    def spawn_enemy_wave(self):
        spawn_count = random.randint(4, 8)

        enemy_pool = [
            (BileSpitter, self.bileSpitterGroup),
            (KamikazeDrone, self.kamikazeDroneGroup),
            (TriSpitter, self.triSpitterGroup),
            (FireLauncher, self.fireLauncherGroup),
            (BladeSpinner, self.bladeSpinnerGroup),
        ]

        # visible screen width in world space
        screen_right = int(self.window_width / self.camera.zoom)

        # spawn slightly inside camera view (top of screen)
        spawn_y = int(self.camera.y) + 5

        for _ in range(spawn_count):
            EnemyClass, group = random.choice(enemy_pool)

            enemy = EnemyClass()

            # -------------------------------
            # 🔑 CRITICAL FIX: FORCE TILED SIZE
            # -------------------------------
            enemy.width = 16
            enemy.height = 16

            enemy.x = random.randint(20, screen_right - 20)
            enemy.y = spawn_y

            enemy.update_hitbox()
            enemy.camera = self.camera
            enemy.target_player = self.starship

            group.append(enemy)

            print(
                f"[SPAWN] {EnemyClass.__name__} "
                f"at x={enemy.x}, y={enemy.y} "
                f"| size=({enemy.width},{enemy.height}) "
                f"| camera.y={int(self.camera.y)}"
            )
