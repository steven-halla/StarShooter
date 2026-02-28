import random
from typing import Optional

import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Bosses.BossLevelThree import BossLevelThree
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.TriSpitter import TriSpitter
from Entity.SpaceStation import SpaceStation
from ScreenClasses.HomeBase import HomeBase
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
        self.prev_enemy_count: int = None
        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.enemy_wave_interval_ms = 7777
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
        self.player_roped:bool = False
        self.trigger_boss3_countdown: bool = False
        self.boss_death_timer = None
        self.level_complete = False



    def start(self, state) -> None:
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
        self.save_state.set_location_level(3, screen_name="Level 3")
        self.save_state.capture_player(self.starship)
        self.save_state.save_to_file("player_save.json")

    def move_map_y_axis(self):
        pass

    def update(self, state) -> None:
        # Create melee_hitbox FIRST (before enemies update)

        if self.boss_death_timer is not None:
            if self.boss_death_timer.is_ready():
                state.starship.money += 30000
                state.currentScreen = HomeBase(self.textbox)
                state.currentScreen.start(state)
                return

        self.starship.melee_hitbox = pygame.Rect(
            int(self.starship.x),
            int(self.starship.y),
            self.starship.width,
            self.starship.height
        )

        self.starship.hitbox = pygame.Rect(0, 0, 0, 0)
        self.starship.update()
        self.update_handle_level_complete(state)

        super().update(state)
        print(len(state.enemies))
        self.update_space_station_collision(state)
        self.update_deflect_hitbox()
        self.update_boss_helper(state)
        self.update_enemy_helper(state)
        if self.trigger_boss3_countdown and not self.boss_spawned:

            if self.boss_spawn_time is None:
                self.boss_spawn_time = pygame.time.get_ticks()

            elif pygame.time.get_ticks() - self.boss_spawn_time >= self.boss_spawn_delay_ms:
                self.spawn_level_3_boss(state)

        # Check if player is caught by rope

        for enemy in state.enemies:
            print("ENEMY COUNT =", len(state.enemies))
            for i, e in enumerate(state.enemies):
                print(i, type(e), getattr(e, "name", None), "id=", id(e))
            if isinstance(enemy, BossLevelThree):
                if getattr(enemy, "player_caught", False):
                    self.player_roped = True
                    print("LEVEL 3: ROPE IS TOUCHING PLAYER")
                break

        # Pull player towards screen corner if roped
        if self.player_roped:
            target_x = self.camera.x
            target_y = self.camera.y

            pull_speed = 2.0  # Adjust this for faster/slower pull

            dx = target_x - self.starship.x
            dy = target_y - self.starship.y

            # Move towards target
            if abs(dx) > 0.5:
                self.starship.x += dx * pull_speed * 0.1
            if abs(dy) > 0.5:
                self.starship.y += dy * pull_speed * 0.1



    # def update(self, state) -> None:
    #     self.starship.hitbox = pygame.Rect(0, 0, 0, 0)
    #     self.starship.update()
    #     super().update(state)
    #     self.update_space_station_collision(state)
    #     self.update_deflect_hitbox()
    #     self.update_boss_helper(state)
    #     self.update_enemy_helper(state)
    #     for enemy in state.enemies:
    #         if enemy.name == "BossLevelThree":
    #             rope = enemy._rope
    #             print(rope)
    #     for enemy in state.enemies:
    #         if enemy.name == "BossLevelThree":
    #             if getattr(enemy, "player_caught", False):
    #                 print("LEVEL 3: ROPE IS TOUCHING PLAYER")

    def draw(self, state):
        super().draw(state)
        self.draw_player_and_enemies_and_space_station(state)
        pygame.display.flip()

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

            if self.space_station is not None:
                station_rect = self.space_station.hitbox

                for enemy in state.enemies:
                    if not isinstance(enemy, BossLevelThree):
                        continue

                    enemy_rect = pygame.Rect(
                        enemy.x,
                        enemy.y,
                        enemy.width,
                        enemy.height
                    )

                    if enemy_rect.colliderect(station_rect):
                        print("ship hit")

                        now = pygame.time.get_ticks()

                        if not hasattr(self, "_station_last_melee_time"):
                            self._station_last_melee_time = 0

                        if now - self._station_last_melee_time >= 3000:
                            self.space_station.hp -= 50
                            self._station_last_melee_time = now

                        enemy.stop_rush()

                        if not hasattr(enemy, "_station_pushback_active"):
                            enemy._station_pushback_active = False

                        if not enemy._station_pushback_active:
                            enemy._station_pushback_active = True
                            enemy._station_pushback_steps_remaining = 4
                            enemy._station_pushback_pixels_per_step = 5
                            enemy._station_pushback_interval_ms = 500
                            enemy._station_pushback_last_step_time = now

                        if enemy._station_pushback_active and enemy._station_pushback_steps_remaining > 0:
                            if now - enemy._station_pushback_last_step_time >= enemy._station_pushback_interval_ms:
                                enemy.y -= enemy._station_pushback_pixels_per_step
                                enemy._station_pushback_steps_remaining -= 1
                                enemy._station_pushback_last_step_time = now
                                enemy.update_hitbox()

                        if hasattr(enemy,
                                   "_station_pushback_steps_remaining") and enemy._station_pushback_steps_remaining <= 0:
                            enemy._station_pushback_active = False

                        enemy.update_hitbox()

            # if self.space_station is not None:
            #     station_rect = self.space_station.hitbox
            #
            #     for enemy in state.enemies:
            #         if not isinstance(enemy, BossLevelThree):
            #             continue
            #
            #         enemy_rect = pygame.Rect(
            #             enemy.x,
            #             enemy.y,
            #             enemy.width,
            #             enemy.height
            #         )
            #
            #         if enemy_rect.colliderect(station_rect):
            #             print("ship hit")
            #
            #             now = pygame.time.get_ticks()
            #
            #             if not hasattr(self, "_station_last_melee_time"):
            #                 self._station_last_melee_time = 0
            #
            #             if now - self._station_last_melee_time >= 3000:
            #                 self.space_station.hp -= 50
            #                 self._station_last_melee_time = now
            #
            #             enemy.stop_rush()
            #             enemy.y -= 20
            #             enemy.update_hitbox()
            #
            # if self.space_station is not None:
            #     station_rect = self.space_station.hitbox
            #
            #     for enemy in state.enemies:
            #         if not isinstance(enemy, BossLevelThree):
            #             continue
            #
            #         enemy_rect = pygame.Rect(
            #             enemy.x,
            #             enemy.y,
            #             enemy.width,
            #             enemy.height
            #         )
            #
            #         if enemy_rect.colliderect(station_rect):
            #             print("ship hit")
            #
            #             now = pygame.time.get_ticks()
            #
            #             if not hasattr(self, "_station_last_melee_time"):
            #                 self._station_last_melee_time = 0
            #
            #             if now - self._station_last_melee_time >= 3000:
            #                 self.space_station.hp -= 50
            #                 self._station_last_melee_time = now
            #
            #             enemy.stop_rush()
            #
            #             overlap_left = enemy_rect.right - station_rect.left
            #             overlap_right = station_rect.right - enemy_rect.left
            #             overlap_top = enemy_rect.bottom - station_rect.top
            #             overlap_bottom = station_rect.bottom - enemy_rect.top
            #             min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            #
            #             if min_overlap == overlap_top:
            #                 enemy.y -= 0.5
            #             elif min_overlap == overlap_bottom:
            #                 enemy.y += 0.5
            #             elif min_overlap == overlap_left:
            #                 enemy.x -= 0.5
            #             elif min_overlap == overlap_right:
            #                 enemy.x += 0.5
            #
            #             enemy.update_hitbox()

        # if self.space_station is not None:
        #     station_rect = self.space_station.hitbox
        #
        #     for enemy in state.enemies:
        #         if not isinstance(enemy, BossLevelThree):
        #             continue
        #
        #         enemy_rect = pygame.Rect(
        #             enemy.x,
        #             enemy.y,
        #             enemy.width,
        #             enemy.height
        #         )
        #
        #         if enemy_rect.colliderect(station_rect):
        #             print("ship hit")
        #             # self.space_station.hp -= 100
        #             now = pygame.time.get_ticks()
        #
        #             if not hasattr(self, "_station_last_melee_time"):
        #                 self._station_last_melee_time = 0
        #
        #             if now - self._station_last_melee_time >= 3000:
        #                 self.space_station.hp -= 50
        #                 self._station_last_melee_time = now
        #
        #             # enemy.stop_rush()
        #
        #             enemy._stop_rush_start_time = pygame.time.get_ticks()
        #             enemy._stop_rush_delay_ms = 5000
        #             enemy._stop_rush_pending = True
        #             if enemy._stop_rush_pending:
        #                 now = pygame.time.get_ticks()
        #                 if now - enemy._stop_rush_start_time >= enemy._stop_rush_delay_ms:
        #                     enemy.stop_rush()
        #
        #                     enemy._stop_rush_pending = False
        #
        #
        #             # push boss out of station
        #             overlap_left = enemy_rect.right - station_rect.left
        #             overlap_right = station_rect.right - enemy_rect.left
        #             overlap_top = enemy_rect.bottom - station_rect.top
        #             overlap_bottom = station_rect.bottom - enemy_rect.top
        #
        #             min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
        #
        #             if min_overlap == overlap_top:
        #                 enemy.y -= min_overlap
        #             elif min_overlap == overlap_bottom:
        #                 enemy.y += min_overlap
        #             elif min_overlap == overlap_left:
        #                 enemy.x -= min_overlap
        #             elif min_overlap == overlap_right:
        #                 enemy.x += min_overlap
        #
        #             enemy.update_hitbox()




            # ... push-out logic ...

    def update_handle_level_complete(self, state):
        if not self.level_complete:
            boss_alive = any(isinstance(enemy, BossLevelThree) for enemy in state.enemies)
            if not boss_alive:
                if self.boss_death_timer is None:
                    self.boss_death_timer = Timer(2.0)
                    self.boss_death_timer.reset()

    def spawn_enemy_drop(self, enemy, state) -> None:
        pass

    def update_enemy_helper(self, state):
        self.enemy_waves_timer(state)
        self.deflect_helper(state)

        for enemy in list(state.enemies):
            enemy.update(state)
            self.clamp_enemy_to_player_view(enemy)  # <-- here

            if hasattr(enemy, "update_hitbox"):
                enemy.update_hitbox()

            if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                state.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            if hasattr(enemy, "enemyHealth") and enemy.enemyHealth <= 0:
                self.remove_enemy_if_dead(enemy, state)

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
                    if getattr(enemy, "name", None) == "kamikaze_drone":
                        self.starship.shield_system.take_damage(enemy.touch_damage)
                        self.starship.on_hit()
                        enemy.enemyHealth = 0
                        self.remove_enemy_if_dead(enemy, state)
                    else:
                        self.starship.shield_system.take_damage(enemy.touch_damage)
                        self.starship.on_hit()
                    break


    def deflect_helper(self, state):
        for bullet in list(state.enemy_bullets):

            # =============================
            # BOMB LOGIC (IMMEDIATE + EXPLOSION)
            # =============================
            if hasattr(bullet, "explosion_radius"):
                bullet_rect = pygame.Rect(
                    bullet.x,
                    bullet.y,
                    bullet.width,
                    bullet.height
                )

                now = pygame.time.get_ticks()

                # ── IMMEDIATE CONTACT DAMAGE ──
                if bullet_rect.colliderect(self.starship.melee_hitbox):
                    self.starship.shield_system.take_damage(bullet.damage)
                    self.starship.on_hit()

                    bullet.exploded = True
                    bullet.explode_time = now

                # ── TIMED / FORCED EXPLOSION ──
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

                continue  # bombs never deflect

            # =============================
            # NORMAL BULLET
            # =============================
            bullet_rect = pygame.Rect(
                bullet.x,
                bullet.y,
                bullet.width,
                bullet.height
            )

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
            # REFLECTED BULLET DAMAGE
            # ─────────────────────────────
            if hasattr(bullet, "is_reflected") and not getattr(bullet, "has_hit_enemy", False):
                for enemy in list(state.enemies):
                    enemy_rect = pygame.Rect(
                        enemy.x,
                        enemy.y,
                        enemy.width,
                        enemy.height
                    )
                    if bullet_rect.colliderect(enemy_rect):
                        enemy.enemyHealth -= bullet.damage
                        bullet.has_hit_enemy = True
                        if bullet in state.enemy_bullets:
                            state.enemy_bullets.remove(bullet)
                        if enemy.enemyHealth <= 0:
                            state.enemies.remove(enemy)
                        break

            # ─────────────────────────────
            # SPACE STATION HIT
            # ─────────────────────────────
            if not hasattr(LevelThree.deflect_helper, "_station_last_hit_time"):
                LevelThree.deflect_helper._station_last_hit_time = 0
            if not hasattr(LevelThree.deflect_helper, "_station_last_melee_time"):
                LevelThree.deflect_helper._station_last_melee_time = 0

            now = pygame.time.get_ticks()

            if self.space_station is not None and bullet_rect.colliderect(self.space_station.hitbox):
                if now - LevelThree.deflect_helper._station_last_hit_time >= 3000:
                    self.space_station.hp -= bullet.damage
                    LevelThree.deflect_helper._station_last_hit_time = now
                if bullet in state.enemy_bullets:
                    state.enemy_bullets.remove(bullet)



    # def deflect_helper(self, state):
    #
    #
    #     for bullet in list(state.enemy_bullets):
    #         if getattr(bullet, "is_bomb", False):
    #             return
    #
    #         bullet_rect = pygame.Rect(
    #             bullet.x,
    #             bullet.y,
    #             bullet.width,
    #             bullet.height
    #         )
    #         if bullet_rect.colliderect(self.deflect_hitbox):
    #             if not hasattr(bullet, "is_reflected"):
    #                 target = self.get_nearest_enemy(bullet)
    #
    #                 if target is None:
    #                     speed = abs(getattr(bullet, "bullet_speed", 4)) * 4
    #                     bullet.vx = 0
    #                     bullet.vy = -speed  # 🔺 FORCE UP
    #                     bullet.is_reflected = True
    #                     bullet.damage = 0
    #                     bullet.update_rect()
    #                 else:
    #                     self.reflect_bullet(bullet)
    #             continue
    #
    #         if hasattr(bullet, "is_reflected"):
    #
    #             enemies = list(state.enemies)
    #             for enemy in enemies:
    #                 enemy_rect = pygame.Rect(
    #                     enemy.x,
    #                     enemy.y,
    #                     enemy.width,
    #                     enemy.height
    #                 )
    #
    #                 if bullet_rect.colliderect(enemy_rect):
    #                     enemy.enemyHealth -= bullet.damage
    #
    #                     if bullet in state.enemy_bullets:
    #                         state.enemy_bullets.remove(bullet)
    #
    #                         if enemy.enemyHealth <= 0:
    #                             state.enemies.remove(enemy)
    #
    #         if not hasattr(LevelThree.deflect_helper, "_station_last_hit_time"):
    #             LevelThree.deflect_helper._station_last_hit_time = 0
    #         if not hasattr(LevelThree.deflect_helper, "_station_last_melee_time"):
    #             LevelThree.deflect_helper._station_last_melee_time = 0
    #
    #         now = pygame.time.get_ticks()
    #
    #         # ─── BULLET DAMAGE ───
    #         if self.space_station is not None and bullet_rect.colliderect(self.space_station.hitbox):
    #             if now - LevelThree.deflect_helper._station_last_hit_time >= 3000:
    #                 self.space_station.hp -= bullet.damage
    #                 LevelThree.deflect_helper._station_last_hit_time = now
    #             if bullet in state.enemy_bullets:
    #                 state.enemy_bullets.remove(bullet)




    def reflect_bullet(self, bullet):
        if getattr(bullet, "is_bomb", False):
            return
        target = self.get_nearest_enemy(bullet)

        speed = abs(getattr(bullet, "bullet_speed", 4)) * 4

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
        if self.boss_spawned or getattr(self, "trigger_boss3_countdown", False):
            return

        now = pygame.time.get_ticks()
        if self.intial_wave and now - self.initial_wave_start_time >= self.initial_wave_delay_ms:
            self.spawn_enemy_wave(state)
            self.intial_wave = False
        if now - self.last_enemy_wave_time >= self.enemy_wave_interval_ms:
            self.spawn_enemy_wave(state)
            self.last_enemy_wave_time = now

    # def enemy_waves_timer(self, state):
    #     now = pygame.time.get_ticks()
    #     if self.intial_wave and now - self.initial_wave_start_time >= self.initial_wave_delay_ms:
    #         self.spawn_enemy_wave(state)
    #         self.intial_wave = False
    #     if now - self.last_enemy_wave_time >= self.enemy_wave_interval_ms:
    #         self.spawn_enemy_wave(state)
    #         self.last_enemy_wave_time = now

    def build_enemy_pool(self, state):
        pool = []

        for enemy in state.enemies:
            if isinstance(enemy, BossLevelThree):
                continue
            if enemy.is_active:
                continue
            pool.append(enemy)

        if not pool:
            self.trigger_boss3_countdown = True

        return pool

    def spawn_enemy_wave(self, state):
        enemy_pool = self.build_enemy_pool(state)

        if not enemy_pool:
            print("[WAVE] No inactive enemies left")
            return

        random.shuffle(enemy_pool)
        spawn_count = min(random.randint(4, 8), len(enemy_pool))
        screen_right = int(self.window_width / self.camera.zoom)
        spawn_y = int(self.camera.y) + 5

        for i in range(spawn_count):
            enemy = enemy_pool[i]

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

    def load_enemy_into_list(self, state):
        state.enemies.clear()

        for obj in self.tiled_map.objects:

            if obj.name == "level_3_boss":
                enemy = BossLevelThree()

            elif obj.name == "bile_spitter":
                enemy = BileSpitter()
            elif obj.name == "blade_spinner":
                enemy = BladeSpinner()
            elif obj.name == "tri_spitter":
                enemy = TriSpitter()
            elif obj.name == "fire_launcher":
                enemy = FireLauncher()
            elif obj.name == "kamikaze_drone":
                enemy = KamikazeDrone()
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

        # pull existing boss from the list (do NOT create a new one)
        boss = next((e for e in state.enemies if isinstance(e, BossLevelThree)), None)
        if boss is None:
            return

        boss.x = (self.window_width / self.camera.zoom) // 2 - boss.width // 2
        boss.y = self.camera.y + 40
        boss.update_hitbox()
        boss.camera = self.camera
        boss.target_player = self.starship

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
