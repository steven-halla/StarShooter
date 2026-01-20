import random
from typing import Optional

import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelThree import BossLevelThree
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.TriSpitter import TriSpitter
from Entity.SpaceStation import SpaceStation
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelThree(VerticalBattleScreen):
    def __init__(self, textbox):
        super().__init__(textbox)
        # self.starship: StarShip = StarShip()

        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level3.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400  # y position of map
        # FIX: GAMEPLAY_HEIGHT is an int, not a (width, height) tuple

        window_height = GlobalConstants.GAMEPLAY_HEIGHT

        self.camera_y = self.WORLD_HEIGHT - window_height
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)

        # window_width, window_height = GlobalConstants.GAMEPLAY_HEIGHT
        #
        # self.camera_y = self.WORLD_HEIGHT - window_height  # look at bottom of map
        # self.camera.world_height = self.WORLD_HEIGHT
        # self.camera.y = float(self.camera_y)

        self.map_scroll_speed_per_frame: float = .4  # move speed of camera

        self.napalm_list: list = []
        self.space_station: Optional[SpaceStation] = None

        self.total_enemies = 40
        self.prev_enemy_count: int = None
        state.enemies_killed: int = 0

        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.enemy_wave_interval_ms = 15000
        self.last_enemy_wave_time = pygame.time.get_ticks()
        # in __init__ of LevelThree
        self.initial_wave_delay_ms = 3000
        self.initial_wave_start_time = pygame.time.get_ticks()
        self.intial_wave = True

        self.boss_spawned = False
        self.boss_spawn_delay_ms = 1000
        self.boss_spawn_time = None
        self.level_start = True
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
        print(state.enemies)
        self.load_space_station_object(state)
        player_x = None
        player_y = None
        self.starship.shipHealth = 100


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

        if self.level_start:
            self.level_start = False
            self.starship.shipHealth = 150
            self.save_state.capture_player(self.starship, self.__class__.__name__)
            self.save_state.save_to_file("player_save.json")

        self.starship.hitbox = pygame.Rect(0, 0, 0, 0)

        # 1️⃣ STARSHIP UPDATE (movement happens here)
        self.starship.update()

        # 2️⃣ RUN BASE SCREEN UPDATE (camera / movement resolution)
        super().update(state)

        # 3️⃣ SPACE STATION COLLISION — AFTER movement is final
        if self.space_station is not None:
            # Update the space station's hitbox
            self.space_station.update_hitbox(state)

            # Custom collision detection that accounts for visual overlap
            # Get the ship's screen position
            ship_screen_x = self.camera.world_to_screen_x(self.starship.x)
            ship_screen_y = self.camera.world_to_screen_y(self.starship.y)
            ship_screen_width = self.starship.width * self.camera.zoom
            ship_screen_height = self.starship.height * self.camera.zoom

            # Get the station's screen position
            station_screen_x = self.camera.world_to_screen_x(self.space_station.x)
            station_screen_y = self.camera.world_to_screen_y(self.space_station.y)
            station_screen_width = self.space_station.width * self.camera.zoom
            station_screen_height = self.space_station.height * self.camera.zoom

            # Create screen-space rectangles
            ship_screen_rect = pygame.Rect(
                int(ship_screen_x),
                int(ship_screen_y),
                int(ship_screen_width),
                int(ship_screen_height)
            )

            station_screen_rect = pygame.Rect(
                int(station_screen_x),
                int(station_screen_y),
                int(station_screen_width),
                int(station_screen_height)
            )

            # Check for collision in screen space
            if ship_screen_rect.colliderect(station_screen_rect):
                # If they collide in screen space, adjust the ship's position in world space
                # to prevent overlap

                # Calculate overlap in screen space
                overlap_left = ship_screen_rect.right - station_screen_rect.left
                overlap_right = station_screen_rect.right - ship_screen_rect.left
                overlap_top = ship_screen_rect.bottom - station_screen_rect.top
                overlap_bottom = station_screen_rect.bottom - ship_screen_rect.top

                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                # Convert screen space overlap to world space
                world_overlap = min_overlap / self.camera.zoom

                # Adjust ship position based on minimum overlap
                if min_overlap == overlap_top:
                    self.starship.y -= world_overlap
                elif min_overlap == overlap_bottom:
                    self.starship.y += world_overlap
                elif min_overlap == overlap_left:
                    self.starship.x -= world_overlap
                elif min_overlap == overlap_right:
                    self.starship.x += world_overlap

                # Update the ship's hitbox after position adjustment
                self.starship.update_hitbox()

        # 4️⃣ MELEE HITBOX (post-movement, post-collision)
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
        for enemy in state.enemies:
            if getattr(enemy, "name", None) == "level_3_boss":
                enemy.check_arm_damage(self.starship)
        # --------------------------------
        # BOSS SPAWN CHECK (SAFE GUARDED)
        # --------------------------------
        if not self.boss_spawned and self.has_no_enemies():

            if self.boss_spawn_time is None:
                self.boss_spawn_time = pygame.time.get_ticks()

            elif pygame.time.get_ticks() - self.boss_spawn_time >= self.boss_spawn_delay_ms:
                self.spawn_level_3_boss()

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

        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)

        if self.space_station is not None:
            self.space_station.draw(state.DISPLAY, self.camera)


        self.draw_ui_panel(state.DISPLAY)

        pygame.display.flip()
    def get_nearest_enemy(self, missile):

        enemies = state.enemies

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




    def enemy_helper(self):
        now = pygame.time.get_ticks()
        # print(
        #     f"BileSpitter: {len(self.bileSpitterGroup)} | "
        #     f"TriSpitter: {len(self.triSpitterGroup)} | "
        #     f"BladeSpinner: {len(self.bladeSpinnerGroup)} | "
        #     f"FireLauncher: {len(self.fireLauncherGroup)} | "
        #     f"KamikazeDrone: {len(self.kamikazeDroneGroup)} | "
        #     f"BossLevelThree: {len(self.bossLevelThreeGroup)}"
        # )
        # in update() of LevelThree (near the top, before enemy logic)
        now = pygame.time.get_ticks()

        if self.intial_wave and now - self.initial_wave_start_time >= self.initial_wave_delay_ms:
            self.spawn_enemy_wave()
            self.intial_wave = False



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
                        # Use the same properties as in reflect_bullet
                        speed = abs(getattr(bullet, "bullet_speed", 4)) * 6
                        bullet.vx = 0
                        bullet.vy = -speed  # 🔺 FORCE UP
                        bullet.is_reflected = True
                        bullet.damage = 0
                        # Update the bullet's rect to ensure proper collision detection
                        bullet.update_rect()
                    else:
                        self.reflect_bullet(bullet)

                continue

            # --------------------------------
            # REFLECTED BULLETS → ENEMIES
            # --------------------------------
            if hasattr(bullet, "is_reflected"):

                enemies = list(state.enemies)

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

                            # death removal
                            if enemy.enemyHealth <= 0:
                                state.enemies.remove(enemy)

            # --------------------------------
            # SPACE STATION DAMAGE
            # --------------------------------
            if self.space_station is not None:
                if bullet_rect.colliderect(self.space_station.hitbox):
                    self.space_station.hp -= bullet.damage
                    if bullet in self.enemy_bullets:
                        self.enemy_bullets.remove(bullet)
                    continue

            # -------------------------
            # METAL SHIELD → ENEMY BULLETS (UNIFIED player_bullets)
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

        # --------------------------------
        # ENEMY UPDATES + BULLET SPAWNING
        # (single unified state.enemies list)
        # --------------------------------
        for enemy in list(state.enemies):
            # common update
            enemy.update()

            # optional hitbox update (only if present)
            if hasattr(enemy, "update_hitbox"):
                enemy.update_hitbox()

            # collect enemy bullets (only if present)
            if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            # remove dead enemies (only if health exists)
            if hasattr(enemy, "enemyHealth") and enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

        # --------------------------------
        # ENEMY BODY COLLISION DAMAGE (LEVEL 3)
        # --------------------------------
        if not self.starship.invincible:
            player_rect = self.starship.melee_hitbox  # ← USE MELEE HITBOX

            enemies = (
                    list(state.enemies)

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
                    if getattr(enemy, "name", None) == "kamikaze_drone":
                        self.starship.shipHealth -= 20
                        self.starship.on_hit()
                        state.enemies.remove(enemy)
                    else:
                        self.starship.shipHealth -= 10
                        self.starship.on_hit()

                    break  # one hit per frame

    def reflect_bullet(self, bullet):
        target = self.get_nearest_enemy(bullet)

        # use existing speed system
        speed = abs(getattr(bullet, "bullet_speed", 4)) * 6

        # --------------------------------
        # NO ENEMY → FORCE STRAIGHT UP
        # --------------------------------
        if target is None:
            bullet.vx = 0
            bullet.vy = -speed
            bullet.is_reflected = True
            bullet.damage = 0
            return

        # Bullet center
        bx = bullet.x + bullet.width / 2
        by = bullet.y + bullet.height / 2

        # Enemy center
        ex = target.x + target.width / 2
        ey = target.y + target.height / 2

        # Direction vector
        dx = ex - bx
        dy = ey - by
        dist = (dx * dx + dy * dy) ** 0.5
        if dist == 0:
            return

        dx /= dist
        dy /= dist

        # ✅ VECTOR VELOCITY
        bullet.vx = dx * speed
        bullet.vy = dy * speed
        bullet.is_reflected = True
        bullet.damage = 100
        # Update the bullet's rect to ensure proper collision detection
        bullet.update_rect()


    def build_enemy_pool(self):
        pool = []

        for group in (
                state.enemies,

        ):
            for enemy in group:
                if not isinstance(enemy, tuple):
                    pool.append(enemy)

        return pool

    def spawn_enemy_wave(self):
        # clean bad data
        for group in (
                state.enemies,

        ):
            group[:] = [e for e in group if not isinstance(e, tuple)]

        # build pool of INACTIVE enemies only
        enemy_pool = self.build_enemy_pool()

        if not enemy_pool:
            print("[WAVE] No inactive enemies left")
            return

        # 🔑 RANDOMIZE ONCE
        random.shuffle(enemy_pool)

        spawn_count = min(random.randint(4, 8), len(enemy_pool))

        screen_right = int(self.window_width / self.camera.zoom)
        spawn_y = int(self.camera.y) + 5

        for i in range(spawn_count):
            enemy = enemy_pool[i]  # ← RANDOM ASSORTMENT

            enemy.x = random.randint(20, screen_right - 20)
            enemy.y = spawn_y
            enemy.is_active = True
            enemy.update_hitbox()

            print(f"[RESPAWN] {enemy.__class__.__name__}")

    # -------------------------------
    # FIX 1: DO NOT LOAD BOSS FROM TMX
    # -------------------------------
    def load_enemy_into_list(self):
        state.enemies.clear()

        for obj in self.tiled_map.objects:
            enemy = None

            # ❌ REMOVE boss loading entirely
            # if obj.name == "level_3_boss":
            #     enemy = BossLevelThree()

            if obj.name == "kamikazi_drone":
                enemy = KamikazeDrone()
            elif obj.name == "bile_spitter":
                enemy = BileSpitter()
            else:
                continue

            enemy.x = obj.x
            enemy.y = obj.y
            enemy.width = obj.width
            enemy.height = obj.height

            enemy.camera = self.camera
            enemy.target_player = self.starship

            if hasattr(enemy, "maxHealth"):
                enemy.enemyHealth = enemy.maxHealth
            else:
                enemy.enemyHealth = 1

            enemy.update_hitbox()
            state.enemies.append(enemy)

    # -------------------------------
    # FIX 2: BOSS SPAWN CONDITION
    # -------------------------------
    def has_no_enemies(self) -> bool:
        return len(state.enemies) == 0

    # -------------------------------
    # FIX 3: SPAWN BOSS ONLY VIA CODE
    # -------------------------------
    def spawn_level_3_boss(self):
        if self.boss_spawned:
            return

        boss = BossLevelThree()

        boss.x = (self.window_width / self.camera.zoom) // 2 - boss.width // 2
        boss.y = self.camera.y + 40

        boss.update_hitbox()
        boss.camera = self.camera
        boss.target_player = self.starship

        state.enemies.append(boss)
        self.boss_spawned = True

    def load_space_station_object(self,state):
        self.space_station = None

        # World Y where the UI panel starts
        ui_top_world_y = (
                self.camera.y
                + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)
        )

        for obj in self.tiled_map.objects:
            if getattr(obj, "name", None) != "space_station":
                continue

            # Place station so its BOTTOM sits just above the UI panel
            station_y = ui_top_world_y - obj.height

            self.space_station = SpaceStation(
                x=obj.x,
                y=station_y,
                width=obj.width,
                height=obj.height,
            )

            self.space_station.update_hitbox(state)
            break
