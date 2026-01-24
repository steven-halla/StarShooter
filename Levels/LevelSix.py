import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelSix import BossLevelSix
from Entity.Monsters.Coins import Coins
from Entity.Monsters.SpikeyBall import SpikeyBall
from SaveStates.SaveState import SaveState
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelSix(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)

        self.level_start:bool = True
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level6.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400 # y position of map
        window_width: int = GlobalConstants.BASE_WINDOW_WIDTH
        window_height: int = GlobalConstants.GAMEPLAY_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - window_height # look at bottom of map
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = .4 # move speed of camera

        self.coins_missed = []


        self.flame_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()



        # state.enemies: list[Enemy] = [] # consolidate all enemies into one list
        # self.load_enemy_into_list()
        self.prev_enemy_count: int = None

        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.game_over: bool = False
        self.level_complete = False

        self.save_state = SaveState()
        self.may_fire_barrage: bool = True
        self.crush_start_time = None
        self.CRUSH_TIME_MS = 500

    def is_boss_on_screen(self) -> bool:
        cam_top = self.camera.y
        cam_bottom = cam_top + GlobalConstants.GAMEPLAY_HEIGHT

        for enemy in state.enemies:
            if not isinstance(enemy, BossLevelSix):
                continue

            boss_top = enemy.y
            boss_bottom = enemy.y + enemy.height

            # World-space overlap check (NO zoom math)
            if boss_bottom >= cam_top and boss_top <= cam_bottom:
                return True

        return False


    def start(self, state) -> None:
        player_x = None
        # self.textbox.show(self.intro_dialogue)
        player_y = None

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break
        self.starship = state.starship

        # Fallback if no player spawn object exists
        if player_x is None or player_y is None:
            # keep existing starship position
            pass
        else:
            self.starship.x = player_x
            self.starship.y = player_y

        self.starship.update_hitbox()
        # self.starship.x = player_x
        # self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list()

    # this is for later for collision blocks and bottom screen squishing player
    def check_player_touching_collision_bottom(self) -> None:
        player = self.starship

        # 1px probe BELOW player
        probe_below = pygame.Rect(
            player.hitbox.x,
            player.hitbox.bottom,
            player.hitbox.width,
            1
        )


    def update(self, state) -> None:
        super().update(state)
        print(self.coins_missed)

        self.check_player_touching_collision_bottom()


        self.assign_single_barrage_owner()
        if len(self.coins_missed) > 9:
            print("game over")


        # print(len(self.coinsGroup))
            # -------------------------
            # COINS (NEW state.enemies PATTERN)
            # -------------------------
        self.player_touches_coin(state)





        if self.level_start == True:
            self.level_start = False
            self.starship.shipHealth = 450
            self.save_state.capture_player(self.starship, self.__class__.__name__)
            self.save_state.save_to_file("player_save.json")

        self.enemy_helper()
        self.extract_object_names()
        self.update_collision_tiles(damage=5)

    def player_touches_coin(self, state):
        for enemy in list(state.enemies):

            if not isinstance(enemy, Coins):
                continue

            # ✅ DO NOT UPDATE COINS HERE
            # Coins are already updated elsewhere in the frame

            # ✅ COIN ↔ PLAYER COLLISION
            if enemy.hitbox.colliderect(self.starship.hitbox):
                print(f"[LAST COIN] x={enemy.x:.2f}, y={enemy.y:.2f}")
                enemy.is_active = False
                state.enemies.remove(enemy)
                continue

            # ✅ SCREEN-SPACE TOP OF UI CHECK (MISS)
            screen_y = self.camera.world_to_screen_y(enemy.y)

            if screen_y > (GlobalConstants.GAMEPLAY_HEIGHT - 1):  # Added 1 point of top padding
                if enemy not in self.coins_missed:
                    self.coins_missed.append(enemy)

                enemy.is_active = False
                state.enemies.remove(enemy)

    def draw(self, state):
        state.DISPLAY.fill((0, 0, 0))  # ← CLEAR SCREEN FIRST
        super().draw(state)
        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        scene_surface = pygame.Surface((window_width, window_height))


        # 2️⃣ Draw TILE OBJECTS (pipes, decorations, etc.)
        for obj in self.tiled_map.objects:
            if hasattr(obj, "image") and obj.image is not None:
                screen_x = self.camera.world_to_screen_x(obj.x)
                screen_y = self.camera.world_to_screen_y(obj.y)
                state.DISPLAY.blit(obj.image, (screen_x, screen_y))

        # 3️⃣ Draw PLAYER
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        # -------------------------
        # DRAW ENEMIES (UNIFIED)
        # -------------------------
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)

            if hasattr(enemy, "draw_damage_flash"):
                enemy.draw_damage_flash(state.DISPLAY, self.camera)

            # Draw barrage for BossLevelSix
            if isinstance(enemy, BossLevelSix):
                enemy.draw_barrage(state.DISPLAY, self.camera)

        self.draw_ui_panel(state.DISPLAY)

        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        # Get state from self
        state = getattr(self, 'state', None)

        if state is None or not state.enemies:
            return None

        # Visible camera bounds (world coordinates)
        visible_top = self.camera.y
        visible_bottom = self.camera.y + (self.window_height / self.camera.zoom)

        nearest_enemy = None
        nearest_dist = float("inf")
        mx, my = missile.x, missile.y

        for enemy in state.enemies:

            if isinstance(enemy, Coins):
                continue

            # ⛔ Skip enemies outside the screen
            if enemy.y + enemy.height < visible_top:
                continue
            if enemy.y > visible_bottom:
                continue

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
        print("🔥 load_enemy_into_list CALLED")

        state.enemies.clear()

        for obj in self.tiled_map.objects:

            # -------------------------
            # BOSS
            # -------------------------
            if obj.name == "level_6_boss":
                enemy = BossLevelSix()

            # -------------------------
            # SPIKEY BALL
            # -------------------------
            elif obj.name == "spikey_ball":
                enemy = SpikeyBall()

            # -------------------------
            # COINS
            # -------------------------
            elif obj.name == "coins":
                enemy = Coins()

            else:
                continue

            # -------------------------
            # COMMON SETUP (ALL ENEMIES)
            # -------------------------
            enemy.x = obj.x
            enemy.y = obj.y
            enemy.width = obj.width
            enemy.height = obj.height
            enemy.camera = self.camera
            enemy.target_player = self.starship
            enemy.update_hitbox()

            state.enemies.append(enemy)

    # FIX: BossLevelSix was being UPDATED TWICE per frame.
    # This causes the damage-flash timer/state to be cleared before draw.
    # Solution: UPDATE EACH BOSS EXACTLY ONCE PER FRAME.

    def enemy_helper(self):

        # -------------------------
        # NAPALM / SHIELD LOGIC (unchanged)
        # -------------------------
        for bullet in list(self.player_bullets):
            if getattr(bullet, "weapon_name", None) != "Napalm Spread":
                continue

            bullet.update()

            if bullet.is_active and bullet.hits(self.starship.hitbox):
                if not self.starship.invincible:
                    self.starship.shipHealth -= bullet.damage
                    self.starship.on_hit()
                bullet.is_active = False

            if not bullet.is_active:
                self.player_bullets.remove(bullet)

        # -------------------------
        # BOSS UPDATE — SINGLE PASS ONLY
        # -------------------------
        for enemy in list(state.enemies):

            if not isinstance(enemy, BossLevelSix):
                continue

            # ✅ UPDATE ONCE
            enemy.update(self.starship)
            enemy.apply_barrage_damage(self.starship)

            if enemy.enemyBullets:
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)
                print("level complete")

        # -------------------------
        # SPIKEY BALLS (unchanged)
        # -------------------------
        for enemy in list(state.enemies):

            if not isinstance(enemy, SpikeyBall):
                continue

            enemy.update()

            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)
                continue

            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)
                if not self.starship.invincible:
                    self.starship.shipHealth -= 5
                    self.starship.on_hit()
            else:
                enemy.color = GlobalConstants.RED




    def draw_level_collision(self, surface: pygame.Surface) -> None:
        self.draw_collision_tiles(surface)

    def assign_single_barrage_owner(self) -> None:
        bosses = [e for e in state.enemies if isinstance(e, BossLevelSix)]

        if not bosses:
            return

        # reset all
        for boss in bosses:
            boss.may_fire_barrage = False

        # choose exactly one
        bosses[0].may_fire_barrage = True
