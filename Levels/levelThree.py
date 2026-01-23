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
from Entity.StarShip import StarShip
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelThree(VerticalBattleScreen):
    def __init__(self, textbox):
        super().__init__(textbox)
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level3.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400  # y position of map
        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - window_height
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = .4  # move speed of camera
        self.space_station: Optional[SpaceStation] = None
        self.total_enemies = 40
        self.prev_enemy_count: int = None
        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.enemy_wave_interval_ms = 15000
        self.last_enemy_wave_time = pygame.time.get_ticks()
        self.initial_wave_delay_ms = 3000
        self.initial_wave_start_time = pygame.time.get_ticks()
        self.intial_wave = True
        self.boss_spawned = False
        self.boss_spawn_delay_ms = 1000
        self.boss_spawn_time = None
        self.level_start = True
        self.game_over: bool = False
        self.disable_player_bullet_damage = True


    def start(self, state) -> None:
        self.load_space_station_object(state)
        self.starship = state.starship
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
        self.load_enemy_into_list(state)
        self.save_state.capture_player(self.starship, self.__class__.__name__)
        self.save_state.save_to_file("player_save.json")

    def move_map_y_axis(self):
        pass

    def update(self, state) -> None:
        self.starship.hitbox = pygame.Rect(0, 0, 0, 0)
        self.starship.update()
        super().update(state)
        self.update_space_station_collision(state)
        self.update_deflect_hitbox()
        self.update_boss_helper(state)
        self.update_enemy_helper(state)

    def draw(self, state):
        super().draw(state)
        self.draw_player_and_enemies_and_space_station(state)
        self.draw_ui_panel(state.DISPLAY)
        pygame.display.flip()



    def update_boss_helper(self, state):
        for enemy in state.enemies:
            if getattr(enemy, "name", None) == "level_3_boss":
                enemy.check_arm_damage(self.starship)

        if not self.boss_spawned and self.has_no_enemies(state):

            if self.boss_spawn_time is None:
                self.boss_spawn_time = pygame.time.get_ticks()

            elif pygame.time.get_ticks() - self.boss_spawn_time >= self.boss_spawn_delay_ms:
                self.spawn_level_3_boss(state)

    def update_deflect_hitbox(self):
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

    def update_space_station_collision(self, state):
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





    def update_enemy_helper(self, state):
        self.enemy_waves_timer(state)

        self.deflect_helper(state)


        for enemy in list(state.enemies):
            # common update
            enemy.update(state)

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

    def deflect_helper(self, state):
        for bullet in list(state.enemy_bullets):

            bullet_rect = pygame.Rect(
                bullet.x,
                bullet.y,
                bullet.width,
                bullet.height
            )
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

                        if bullet in state.enemy_bullets:
                            state.enemy_bullets.remove(bullet)

                            # death removal
                            if enemy.enemyHealth <= 0:
                                state.enemies.remove(enemy)

            # --------------------------------
            # SPACE STATION DAMAGE
            # --------------------------------
            if self.space_station is not None:
                if bullet_rect.colliderect(self.space_station.hitbox):
                    self.space_station.hp -= bullet.damage
                    if bullet in state.enemy_bullets:
                        state.enemy_bullets.remove(bullet)
                    continue



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

    def enemy_waves_timer(self, state):
        now = pygame.time.get_ticks()
        if self.intial_wave and now - self.initial_wave_start_time >= self.initial_wave_delay_ms:
            self.spawn_enemy_wave(state)
            self.intial_wave = False
        if now - self.last_enemy_wave_time >= self.enemy_wave_interval_ms:
            self.spawn_enemy_wave()
            self.last_enemy_wave_time = now


    def build_enemy_pool(self, state):
        pool = []

        for group in (
                state.enemies,

        ):
            for enemy in group:
                if not isinstance(enemy, tuple):
                    pool.append(enemy)

        return pool

    def spawn_enemy_wave(self, state):
        # clean bad data
        for group in (
                state.enemies,

        ):
            group[:] = [e for e in group if not isinstance(e, tuple)]

        # build pool of INACTIVE enemies only
        enemy_pool = self.build_enemy_pool(state)

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

    def draw_player_and_enemies_and_space_station(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)
        if self.space_station is not None:
            self.space_station.draw(state.DISPLAY, self.camera)
    # -------------------------------
    # FIX 1: DO NOT LOAD BOSS FROM TMX
    # -------------------------------
    def load_enemy_into_list(self, state):
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
    def has_no_enemies(self, state) -> bool:
        return len(state.enemies) == 0

    # -------------------------------
    # FIX 3: SPAWN BOSS ONLY VIA CODE
    # -------------------------------
    def spawn_level_3_boss(self, state):
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

