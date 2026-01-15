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
        # self.starship: StarShip = StarShip()

        self.level_start:bool = True
        self.current_page_lines: list[list[str]] = []
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

        self.coinsGroup: list[Coins] = []
        self.spikeyBallGroup: list[SpikeyBall] = []
        self.bossLevelSixGroup: list[BossLevelSix] = []

        self.coins_missed = []

        self.flame_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()



        # self.enemies: list[Enemy] = [] # consolidate all enemies into one list
        # self.load_enemy_into_list()
        self.napalm_list: list = []
        self.wind_slicer_list: list = []
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

        for boss in self.bossLevelSixGroup:
            boss_top = boss.y
            boss_bottom = boss.y + boss.height

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
        print("=== ENEMIES ===")

        print(f"Gold Coins ({len(self.coinsGroup)}):")
        for i, coin in enumerate(self.coinsGroup):
            print(f"  [{i}] Coins @ (x={coin.x}, y={coin.y})")

        print(f"\nBoss 6 ({len(self.bossLevelSixGroup)}):")
        for i, boss in enumerate(self.bossLevelSixGroup):
            print(f"  [{i}] BossLevelSix @ (x={boss.x}, y={boss.y})")

        print(f"\nSpikey Balls ({len(self.spikeyBallGroup)}):")
        for i, ball in enumerate(self.spikeyBallGroup):
            print(f"  [{i}] SpikeyBall @ (x={ball.x}, y={ball.y})")

        print("================\n")
        self.check_player_touching_collision_bottom()


        self.assign_single_barrage_owner()
        if len(self.coinsGroup) > 9:
            print("game over")


        # print(len(self.coinsGroup))
        for coin in list(self.coinsGroup):
            coin.update()

            # SCREEN-space bottom (this bypasses Enemy._clamp_vertical)
            screen_y = self.camera.world_to_screen_y(coin.y)

            if screen_y > GlobalConstants.GAMEPLAY_HEIGHT:
                if coin not in self.coins_missed:
                    self.coins_missed.append(coin)
                coin.is_active = False
                self.coinsGroup.remove(coin)
                continue

            if self.starship.hitbox.colliderect(coin.hitbox):
                coin.enemyHealth = 0
                coin.is_active = False
                self.remove_enemy_if_dead(coin)





        if self.level_start == True:
            self.level_start = False
            self.starship.shipHealth = 450
            self.save_state.capture_player(self.starship, self.__class__.__name__)
            self.save_state.save_to_file("player_save.json")

        self.enemy_helper()
        self.extract_object_names()
        self.update_collision_tiles(damage=5)

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
        for coin in self.coinsGroup:
            coin.draw(state.DISPLAY, self.camera)


        for enemy in self.spikeyBallGroup:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        for boss in self.bossLevelSixGroup:
            boss.draw(state.DISPLAY, self.camera)
            boss.draw_damage_flash(state.DISPLAY, self.camera)


        self.draw_ui_panel(state.DISPLAY)

        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        enemies = (
                # Excluding rescue pods from missile targeting


                list(self.spikeyBallGroup) +

                list(self.bossLevelSixGroup)
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
        print("🔥 load_enemy_into_list CALLED")

        self.coinsGroup.clear()
        self.spikeyBallGroup.clear()
        self.bossLevelSixGroup.clear()
        print(f"BossLevelSixGroup count = {len(self.bossLevelSixGroup)}")

        for obj in self.tiled_map.objects:
            # ⭐ LOAD ENEMIES (existing code)
            if obj.name == "level_6_boss":
                enemy = BossLevelSix()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.bossLevelSixGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
            # LOAD COINS (LevelSix.load_enemy_into_list)

            if obj.name == "spikey_ball":
                enemy = SpikeyBall()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.spikeyBallGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship

            if obj.name == "coins":
                enemy = Coins()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.coinsGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship















    def enemy_helper(self):



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
        for boss in list(self.bossLevelSixGroup):

            boss.update()
            boss.apply_barrage_damage(self.starship)

            if boss.enemyBullets:
                self.enemy_bullets.extend(boss.enemyBullets)
                boss.enemyBullets.clear()

            if boss.enemyHealth <= 0:
                self.bossLevelSixGroup.remove(boss)
                print("level complete")







        # -------------------------
        # wasp stingers
        # -------------------------
        for ball in list(self.spikeyBallGroup):

            ball.update()

            if ball.enemyHealth <= 0:
                self.spikeyBallGroup.remove(ball)
                continue

            # Check collision with player
            if self.starship.hitbox.colliderect(ball.hitbox):
                # Change color to indicate collision
                ball.color = (135, 206, 235)
                # Apply damage to player if not invincible
                if not self.starship.invincible:
                    self.starship.shipHealth -= 5  # Damage amount
                    self.starship.on_hit()
            else:
                ball.color = GlobalConstants.RED





    def draw_level_collision(self, surface: pygame.Surface) -> None:
        self.draw_collision_tiles(surface)

    def assign_single_barrage_owner(self) -> None:
        if not self.bossLevelSixGroup:
            return

        # reset all
        for boss in self.bossLevelSixGroup:
            boss.may_fire_barrage = False

        # choose exactly one
        self.bossLevelSixGroup[0].may_fire_barrage = True
