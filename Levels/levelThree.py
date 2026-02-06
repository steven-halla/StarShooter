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
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level3.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400  # y position of map
        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - window_height
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = 0   # move speed of camera
        self.space_station: Optional[SpaceStation] = None
        self.prev_enemy_count: int = None
        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.enemy_wave_interval_ms = 555
        self.last_enemy_wave_time = pygame.time.get_ticks()
        self.initial_wave_delay_ms = 555
        self.initial_wave_start_time = pygame.time.get_ticks()
        self.intial_wave = True
        self.boss_spawned = False
        self.boss_spawn_delay_ms = 300
        self.boss_spawn_time = None
        self.level_start = True
        self.game_over: bool = False
        self.disable_player_bullet_damage = True
        self.any_enemy_has_been_active = False
        self.trigger_boss3_countdown: bool = False
        self.force_player_slam = False
        self.slam_x = 0
        self.slam_y = 0

    def slam_player_to_corner(self, state) -> None:
        self.force_player_slam = True
        self.slam_x = self.camera.world_x
        self.slam_y = self.camera.world_y
    def start(self, state) -> None:
        self.map_scroll_speed_per_frame: float = 0   # move speed of camera

        self.load_space_station_object(state)
        self.starship = state.starship
        player_x = None
        player_y = None
        self.starship.current_level = 3


        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break

        if "Wind Slicer" not in state.starship.magic_inventory:
            state.starship.magic_inventory.append("Wind Slicer")
        state.starship.equipped_magic = ["Wind Slicer", None]

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list(state)
        self.save_state.capture_player(self.starship)
        self.save_state.save_to_file("player_save.json")


    def move_map_y_axis(self):
        pass

    def update(self, state) -> None:
        self.starship.hitbox = pygame.Rect(0, 0, 0, 0)
        self.starship.update()
        super().update(state)
        self.update_space_station_collision(state)
        self.update_deflect_hitbox()
        # self.update_boss_helper(state)
        self.update_enemy_helper(state)

        for enemy in state.enemies:
            if isinstance(enemy, BossLevelThree) and enemy.player_caught:

                # TARGET = top-left of camera (world space)
                target_x = self.camera.x
                target_y = self.camera.y

                # CURRENT player position
                px = state.starship.x
                py = state.starship.y

                # VECTOR toward corner
                dx = target_x - px
                dy = target_y - py

                # distance to target
                dist = (dx * dx + dy * dy) ** 0.5

                # how fast the slam pulls (tweak this)
                slam_speed = 10.0

                if dist > slam_speed:
                    # normalize and move smoothly
                    dx /= dist
                    dy /= dist
                    state.starship.x += dx * slam_speed
                    state.starship.y += dy * slam_speed
                else:
                    # close enough → snap + finish
                    state.starship.x = target_x
                    state.starship.y = target_y
                    enemy.player_caught = False  # stop pulling

                state.starship.update_hitbox()
                break
        on_screen = []

        view_left = self.camera.x
        view_right = self.camera.x + (self.window_width / self.camera.zoom)
        view_top = self.camera.y
        view_bottom = self.camera.y + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)

        for e in state.enemies:
            if (
                    e.x + e.width >= view_left
                    and e.x <= view_right
                    and e.y + e.height >= view_top
                    and e.y <= view_bottom
            ):
                on_screen.append(
                    f"{e.__class__.__name__}"
                    f"(x={e.x:.1f}, y={e.y:.1f}, "
                    f"screen_y={e.y - self.camera.y:.1f}, "
                    f"active={e.is_active})"
                )

        # print(f"[BOSS CHECK] Enemies ACTUALLY on screen: {on_screen}")
        # on_screen = [
        #     f"{e.__class__.__name__}(x={e.x:.1f}, y={e.y:.1f}, active={e.is_active})"
        #     for e in state.enemies
        #     if e.is_on_screen
        # ]
        #
        # print(f"[BOSS CHECK] Enemies on screen with player: {on_screen}")
        # print(state.enemies)
        # print(len(state.enemies))
        if self.trigger_boss3_countdown and not self.boss_spawned:

            if self.boss_spawn_time is None:
                self.boss_spawn_time = pygame.time.get_ticks()

            elif pygame.time.get_ticks() - self.boss_spawn_time >= self.boss_spawn_delay_ms:
                self.spawn_level_3_boss(state)




    def draw(self, state):
        super().draw(state)
        self.draw_player_and_enemies_and_space_station(state)
        self.draw_ui_panel(state.DISPLAY)
        pygame.display.flip()


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
        if self.space_station is not None:
            self.space_station.update_hitbox(state)

            ship_screen_x = self.camera.world_to_screen_x(self.starship.x)
            ship_screen_y = self.camera.world_to_screen_y(self.starship.y)
            ship_screen_width = self.starship.width * self.camera.zoom
            ship_screen_height = self.starship.height * self.camera.zoom

            station_screen_x = self.camera.world_to_screen_x(self.space_station.x)
            station_screen_y = self.camera.world_to_screen_y(self.space_station.y)
            station_screen_width = self.space_station.width * self.camera.zoom
            station_screen_height = self.space_station.height * self.camera.zoom

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

            if ship_screen_rect.colliderect(station_screen_rect):
                overlap_left = ship_screen_rect.right - station_screen_rect.left
                overlap_right = station_screen_rect.right - ship_screen_rect.left
                overlap_top = ship_screen_rect.bottom - station_screen_rect.top
                overlap_bottom = station_screen_rect.bottom - ship_screen_rect.top
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                world_overlap = min_overlap / self.camera.zoom

                if min_overlap == overlap_top:
                    self.starship.y -= world_overlap
                elif min_overlap == overlap_bottom:
                    self.starship.y += world_overlap
                elif min_overlap == overlap_left:
                    self.starship.x -= world_overlap
                elif min_overlap == overlap_right:
                    self.starship.x += world_overlap

                self.starship.update_hitbox()

    def clamp_enemy_to_player_view(self, enemy) -> None:
        # ❌ NEVER pull enemies onto the screen
        if not enemy.is_on_screen:
            return

        # CAMERA VIEW (WORLD SPACE)
        view_left = self.camera.x
        view_right = self.camera.x + (self.window_width / self.camera.zoom)
        view_top = self.camera.y
        view_bottom = self.camera.y + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)

        # HORIZONTAL CLAMP
        if enemy.x < view_left:
            enemy.x = view_left
        elif enemy.x + enemy.width > view_right:
            enemy.x = view_right - enemy.width

        # VERTICAL CLAMP
        if enemy.y < view_top:
            enemy.y = view_top
        elif enemy.y + enemy.height > view_bottom:
            enemy.y = view_bottom - enemy.height

        enemy.update_hitbox()

    def update_enemy_helper(self, state):
        self.enemy_waves_timer(state)
        self.deflect_helper(state)

        now = pygame.time.get_ticks()

        for enemy in list(state.enemies):

            # 🧊 SPAWN FREEZE (1 second, ONE-TIME)
            if hasattr(enemy, "spawn_time"):
                if now - enemy.spawn_time < enemy.spawn_grace_ms:
                    # keep hitbox valid but DO NOT early-exit forever
                    enemy.update_hitbox()
                    continue
                else:
                    # 🔑 IMPORTANT: clear spawn freeze so enemy resumes normal life
                    del enemy.spawn_time
                    del enemy.spawn_grace_ms

            # ✅ NORMAL UPDATE AFTER FREEZE
            enemy.update(state)

            if not enemy.is_active:
                continue

            # self.clamp_enemy_to_world(enemy)
            self.clamp_enemy_to_player_view(enemy)

            if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                state.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            if hasattr(enemy, "enemyHealth") and enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

        # PLAYER CONTACT DAMAGE
        if not self.starship.invincible:
            player_rect = self.starship.melee_hitbox

            for enemy in list(state.enemies):
                enemy_rect = pygame.Rect(
                    enemy.x,
                    enemy.y,
                    enemy.width,
                    enemy.height
                )
                if player_rect.colliderect(enemy_rect):
                    if hasattr(enemy, "touch_damage"):
                        old_health = self.starship.shipHealth
                        self.starship.shield_system.take_damage(enemy.touch_damage)
                        if self.starship.shipHealth < old_health:
                            self.starship.on_hit()
                    break

    def deflect_helper(self, state):
        for bullet in list(state.enemy_bullets):

            bullet_rect = pygame.Rect(
                bullet.x,
                bullet.y,
                bullet.width,
                bullet.height
            )

            now = pygame.time.get_ticks()

            # =============================
            # 💣 BOMB / EXPLOSION DAMAGE
            # =============================
            if hasattr(bullet, "explosion_radius"):
                # immediate contact damage
                if bullet_rect.colliderect(self.starship.melee_hitbox):
                    self.starship.shield_system.take_damage(bullet.damage)
                    self.starship.on_hit()
                    bullet.exploded = True
                    bullet.explode_time = now

                # timed explosion
                if not getattr(bullet, "exploded", False) and now >= bullet.explode_time:
                    bullet.exploded = True

                if getattr(bullet, "exploded", False):
                    explosion_rect = pygame.Rect(
                        bullet.x - bullet.explosion_radius,
                        bullet.y - bullet.explosion_radius,
                        bullet.explosion_radius * 2,
                        bullet.explosion_radius * 2
                    )

                    if explosion_rect.colliderect(self.starship.melee_hitbox):
                        self.starship.shield_system.take_damage(bullet.damage)
                        self.starship.on_hit()

                    if bullet in state.enemy_bullets:
                        state.enemy_bullets.remove(bullet)

                continue  # 🚫 bombs NEVER deflect

            # =============================
            # 🔑 DEFLECTABLE BULLETS ONLY
            # =============================
            if getattr(bullet, "can_deflect", True) is False:
                continue

            # ─────────────────────────────
            # DEFLECT CHECK
            # ─────────────────────────────
            if bullet_rect.colliderect(self.deflect_hitbox):
                if not hasattr(bullet, "is_reflected"):
                    target = self.get_nearest_enemy(bullet)
                    speed = abs(getattr(bullet, "bullet_speed", 4)) * 6

                    if target is None:
                        bullet.vx = 0
                        bullet.vy = -speed
                        bullet.damage = 0
                    else:
                        self.reflect_bullet(bullet)

                    bullet.is_reflected = True
                    bullet.has_hit_enemy = False
                    bullet.update_rect()

                continue

            # ─────────────────────────────
            # REFLECTED BULLET → ENEMY
            # ─────────────────────────────
            if hasattr(bullet, "is_reflected") and not getattr(bullet, "has_hit_enemy", False):
                for enemy in list(state.enemies):
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)

                    if bullet_rect.colliderect(enemy_rect):
                        enemy.enemyHealth -= bullet.damage
                        bullet.has_hit_enemy = True

                        if bullet in state.enemy_bullets:
                            state.enemy_bullets.remove(bullet)

                        if enemy.enemyHealth <= 0:
                            state.enemies.remove(enemy)

                        break
    # def deflect_helper(self, state):
    #     for bullet in list(state.enemy_bullets):
    #
    #         # =============================
    #         # 🔑 BOMB LOGIC (IMMEDIATE + EXPLOSION)
    #         # =============================
    #         if hasattr(bullet, "explosion_radius"):
    #             bullet_rect = pygame.Rect(
    #                 bullet.x,
    #                 bullet.y,
    #                 bullet.width,
    #                 bullet.height
    #             )
    #
    #             now = pygame.time.get_ticks()
    #
    #             # ── IMMEDIATE CONTACT DAMAGE ──
    #             if bullet_rect.colliderect(self.starship.melee_hitbox):
    #                 self.starship.shield_system.take_damage(bullet.damage)
    #                 self.starship.on_hit()
    #
    #                 # trigger explosion immediately
    #                 bullet.exploded = True
    #                 bullet.explode_time = now
    #
    #             # ── TIMED / FORCED EXPLOSION ──
    #             if not getattr(bullet, "exploded", False) and now >= bullet.explode_time:
    #                 bullet.exploded = True
    #
    #             if getattr(bullet, "exploded", False):
    #                 explosion_rect = pygame.Rect(
    #                     bullet.x - bullet.explosion_radius,
    #                     bullet.y - bullet.explosion_radius,
    #                     bullet.explosion_radius * 2,
    #                     bullet.explosion_radius * 2
    #                 )
    #
    #                 if explosion_rect.colliderect(self.starship.melee_hitbox):
    #                     self.starship.shield_system.take_damage(bullet.damage)
    #                     self.starship.on_hit()
    #
    #                 if bullet in state.enemy_bullets:
    #                     state.enemy_bullets.remove(bullet)
    #
    #             continue  # bombs never deflect

            # =============================
            # NORMAL BULLET

    def reflect_bullet(self, bullet):
        # =============================
        # 🔑 NEVER REFLECT BOMBS
        # =============================
        if hasattr(bullet, "explosion_radius"):
            return

        target = self.get_nearest_enemy(bullet)
        speed = abs(getattr(bullet, "bullet_speed", 4))

        if target is None:
            bullet.vx = 0
            bullet.vy = -speed
            bullet.is_reflected = True
            bullet.damage = 0
            return

        bx = bullet.x + bullet.width / 2
        by = bullet.y + bullet.height / 2
        ex = target.x + target.width / 2
        ey = target.y + target.height / 2

        dx = ex - bx
        dy = ey - by
        dist = (dx * dx + dy * dy) ** 0.5
        if dist == 0:
            return

        dx /= dist
        dy /= dist

        bullet.vx = dx * speed
        bullet.vy = dy * speed
        bullet.is_reflected = True
        bullet.damage = 100
        bullet.update_rect()
    def enemy_waves_timer(self, state):
        now = pygame.time.get_ticks()
        if self.intial_wave and now - self.initial_wave_start_time >= self.initial_wave_delay_ms:
            self.spawn_enemy_wave(state)
            self.intial_wave = False
            print("Called")

        if now - self.last_enemy_wave_time >= self.enemy_wave_interval_ms:
            self.spawn_enemy_wave(state)
            self.last_enemy_wave_time = now
            print("Walled")
    #
    # def build_enemy_pool(self, state):
    #     pool = []
    #
    #     for group in (
    #             state.enemies,
    #     ):
    #         for enemy in group:
    #             if isinstance(enemy, tuple):
    #                 continue
    #             if isinstance(enemy, BossLevelThree):
    #                 continue
    #             pool.append(enemy)
    #
    #     if not pool:
    #         self.trigger_boss3_countdown = True
    #
    #     return pool
    def build_enemy_pool(self, state):
        pool = []

        for enemy in state.enemies:
            # never touch bosses
            if isinstance(enemy, BossLevelThree):
                continue

            # 🔑 DO NOT reuse active enemies (prevents teleporting)
            if enemy.is_active:
                continue

            pool.append(enemy)

        # no enemies left → boss countdown
        if not pool:
            self.trigger_boss3_countdown = True

        return pool

    def spawn_enemy_wave(self, state):
        # Remove invalid entries and bosses
        for group in (state.enemies,):
            group[:] = [
                e for e in group
                if not isinstance(e, tuple)
            ]

        enemy_pool = self.build_enemy_pool(state)
        if not enemy_pool:
            return

        random.shuffle(enemy_pool)
        spawn_count = min(random.randint(4, 8), len(enemy_pool))

        # CAMERA VIEW (WORLD SPACE)
        view_left = self.camera.x
        view_right = self.camera.x + (self.window_width / self.camera.zoom)

        # SPAWN Y: 300 ABOVE SPACE STATION (fallback to player)
        if self.space_station is not None:
            spawn_y = self.space_station.y - 600
        else:
            spawn_y = self.starship.x + 40

        for i in range(spawn_count):
            enemy = enemy_pool[i]

            enemy.x = random.randint(
                int(view_left + 20),
                int(view_right - enemy.width - 20)
            )
            enemy.y = spawn_y
            enemy.is_active = True

            # SPAWN GRACE
            enemy.spawn_time = pygame.time.get_ticks()
            enemy.spawn_grace_ms = 2000

            # ONE-TIME SAFETY CLAMP
            enemy.update_hitbox()

            view_top = self.camera.y
            view_bottom = self.camera.y + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)

            if enemy.y < view_top:
                enemy.y = view_top + 20
            elif enemy.y + enemy.height > view_bottom:
                enemy.y = view_bottom - enemy.height - 20

            enemy.update_hitbox()
    # def spawn_enemy_wave(self, state):
    #     for group in (
    #             state.enemies,
    #
    #     ):
    #         group[:] = [e for e in group if not isinstance(e, tuple)]
    #
    #     enemy_pool = self.build_enemy_pool(state)
    #
    #     if not enemy_pool:
    #         # print("[WAVE] No inactive enemies left")
    #         return
    #
    #     random.shuffle(enemy_pool)
    #     spawn_count = min(random.randint(4, 8), len(enemy_pool))
    #     screen_right = int(self.window_width / self.camera.zoom)
    #     spawn_y = int(self.camera.y) + 5
    #
    #     for i in range(spawn_count):
    #         enemy = enemy_pool[i]  # ← RANDOM ASSORTMENT
    #
    #         enemy.x = random.randint(20, screen_right - 20)
    #         enemy.y = spawn_y
    #         enemy.is_active = True
    #         enemy.update_hitbox()

            # print(f"[RESPAWN] {enemy.__class__.__name__}")

    def draw_player_and_enemies_and_space_station(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)
        if self.space_station is not None:
            self.space_station.draw(state.DISPLAY, self.camera)

    def load_enemy_into_list(self, state):
        state.enemies.clear()

        for obj in self.tiled_map.objects:


            # if obj.name == "tri_spitter":
            #     enemy = TriSpitter()
            # elif obj.name == "bile_spitter":
            #     enemy = BileSpitter()
            # elif obj.name == "blade_spinner":
            #     enemy = BladeSpinner()
            # elif obj.name == "fire_launcher":
            #     enemy = FireLauncher()
            # elif obj.name == "kamikaze_drone":
            #     enemy = KamikazeDrone()
            if obj.name == "level_3_boss":
                enemy = BossLevelThree()
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

    def has_no_enemies(self, state) -> bool:
        return len(state.enemies) == 0

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

        ui_top_world_y = (
                self.camera.y
                + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)
        )

        for obj in self.tiled_map.objects:
            if getattr(obj, "name", None) != "space_station":
                continue

            station_y = ui_top_world_y - obj.height

            self.space_station = SpaceStation(
                x=obj.x,
                y=station_y,
                width=obj.width,
                height=obj.height,
            )

            self.space_station.update_hitbox(state)
            break

