import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.TriSpitter import TriSpitter
from SaveStates.SaveState import SaveState
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen

# as an option have different dialog options based on how many you miss on waht part of stage

class LevelOne(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        # self.starship: StarShip = StarShip()
        self.has_entered_screen = False
        self.level_start:bool = True
        self.current_page_lines: list[list[str]] = []
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level1.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height

        # WORLD HEIGHT (keep +400 as intended)
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400

        window_width: int = GlobalConstants.BASE_WINDOW_WIDTH
        window_height: int = GlobalConstants.GAMEPLAY_HEIGHT

        # 🔧 FIX: camera start must respect ZOOMED visible height
        visible_height = window_height / self.camera.zoom
        self.camera_y = self.WORLD_HEIGHT - visible_height

        # 🔧 FIX: sync camera limits AFTER WORLD_HEIGHT change
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - (window_height / self.camera.zoom)
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = .4  # move speed of camera

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
        self.save_state = SaveState()

        self.intro_dialogue = (
            "I am the ultimate man on the battlefield. "
            "You cannot hope to win against the likes of me. "
            "Prepare yourself, dum dum mortal head. "
            "Bla bla bla bla bla. "
            "Win against the likes of me if you dare."
        )

    def start(self, state) -> None:
        print("I only want to see this one time")
        player_x = None
        # self.textbox.show(self.intro_dialogue)
        player_y = None

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break
        self.starship = state.starship

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list(state)

    def update(self, state) -> None:
        super().update(state)
        # print(self.missed_enemies)
        if not hasattr(self, "last_enemy_count"):
            self.last_enemy_count = len(state.enemies)


        self.bullet_helper(state)

        # if len(state.enemies) < self.last_enemy_count:
        #     print(
        #         f"[WARNING] enemies SHRANK "
        #         f"{self.last_enemy_count} → {len(state.enemies)}"
        #     )

        self.last_enemy_count = len(state.enemies)
        # print(f"[ENEMIES] count={len(state.enemies)}")
        # for i, enemy in enumerate(state.enemies):
        #     print(f"{i}: {enemy.__class__.__name__} at ({enemy.x}, {enemy.y}) hp={enemy.enemyHealth}")

        if len(self.missed_enemies) > 9:
            print("GAME OVER!!!")
            self.game_over = True

        if self.level_start == True:
            self.level_start = False
            self.starship.shipHealth = 144

            self.save_state.capture_player(self.starship, self.__class__.__name__)
            self.save_state.save_to_file("player_save.json")



        now = pygame.time.get_ticks()
        elapsed = now - self.level_start_time

        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        SCREEN_TOP = 0
        SCREEN_BOTTOM = GlobalConstants.BASE_WINDOW_HEIGHT

        screen_height = self.camera.window_height
        UI_KILL_PADDING = 13.5 # pixels ABOVE the UI panel (tweak this)

        screen_bottom = (
                self.camera.y
                + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)
                - UI_KILL_PADDING
        )

        for enemy in list(state.enemies):
            # enemy is BELOW visible gameplay area
            if enemy.y > screen_bottom:
                if enemy not in self.missed_enemies:
                    self.missed_enemies.append(enemy)
                    print(self.missed_enemies)
                    if self.missed_enemies.__len__() > 3:
                        print("GAME OVER!!!")

        self.enemy_helper(state)

        self.extract_object_names()
        if self.level_complete:
            next_level = MissionBriefingScreenLevelTwo()
            # next_level.set_player(state.starship)
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
        current_enemies = len(state.enemies)

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

        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)



        self.draw_ui_panel(state.DISPLAY)
        # self.textbox.show("I am the ultimate man on the battlefiled. You cannot hope to win aginst the likes of me, prepare yourself dum dum mortal head. bla bla bal bal bla; win  the likes of me, prepare yourself dum dum mortal head. bla bla bal bal bla")

        # self.textbox.draw(state.DISPLAY)

        pygame.display.flip()

    def get_nearest_enemy(self, state, missile):
        if not state.enemies:
            return None

        # Visible camera bounds (world coordinates)
        visible_top = self.camera.y
        visible_bottom = self.camera.y + (self.window_height / self.camera.zoom)

        nearest_enemy = None
        nearest_dist_sq = float("inf")

        missile_x = missile.x
        missile_y = missile.y

        for enemy in state.enemies:

            # skip enemies outside screen
            if enemy.y + enemy.height < visible_top:
                continue
            if enemy.y > visible_bottom:
                continue

            # VECTOR distance (vx / vy)
            vx = enemy.x - missile_x
            vy = enemy.y - missile_y

            dist_sq = vx * vx + vy * vy

            if dist_sq < nearest_dist_sq:
                nearest_dist_sq = dist_sq
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

    def load_enemy_into_list(self, state):
        state.enemies.clear()
        # print("[LOAD] clearing enemies list")

        for obj in self.tiled_map.objects:
            enemy = None

            print(f"[TMX] found object name={obj.name} at ({obj.x}, {obj.y})")

            if obj.name == "level_1_boss":
                enemy = BossLevelOne()
            elif obj.name == "bile_spitter":
                enemy = BileSpitter()
            elif obj.name == "blade_spinner":
                enemy = BladeSpinner()
            elif obj.name == "tri_spitter":
                enemy = TriSpitter()
            else:
                # print("[SKIP] object not an enemy")
                continue

            # position / size
            enemy.x = obj.x
            enemy.y = obj.y
            enemy.width = obj.width
            enemy.height = obj.height

            # REQUIRED state
            enemy.camera = self.camera
            enemy.target_player = self.starship

            # 🔑 CRITICAL FIX: ensure health is initialized
            if hasattr(enemy, "maxHealth"):
                enemy.enemyHealth = enemy.maxHealth
            else:
                enemy.enemyHealth = 1  # safe fallback

            enemy.update_hitbox()

            state.enemies.append(enemy)
            print(
                f"[ADD] {enemy.__class__.__name__} "
                f"hp={enemy.enemyHealth} "
                f"→ enemies size = {len(state.enemies)}"
            )

        print(f"[DONE] total enemies loaded = {len(state.enemies)}")


    def enemy_helper(self, state):

        # screen bottom in WORLD coordinates
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)



        for enemy in list(state.enemies):

            # off-screen → missed
            if enemy.y > screen_bottom:
                if enemy not in self.missed_enemies:
                    self.missed_enemies.append(enemy)
                    print("enemy missed")
                continue

            # update enemy
            enemy.update(state)

            # color change on player collision (same logic as before)
            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)
            else:
                enemy.color = GlobalConstants.RED

            enemy.update_hitbox()

            # emit enemy bullets (same behavior as before)
            if state.enemy_bullets and hasattr(enemy, 'enemy_bullets'):
                state.enemy_bullets.extend(enemy.enemy_bullets)
                enemy.enemy_bullets.clear()

            # death removal
            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

    def bullet_helper(self, state):
        for bullet in list(state.player_bullets):

            # -------------------------
            # METAL SHIELD (uses rect, not hitbox)
            # -------------------------
            if bullet.weapon_name == "Metal Shield":
                shield_rect = bullet.rect

                for enemy in list(state.enemies):
                    if shield_rect.colliderect(enemy.hitbox):
                        enemy.enemyHealth -= bullet.damage
                        if enemy.enemyHealth <= 0:
                            self.remove_enemy_if_dead(enemy)
                continue

            # -------------------------
            # ALL OTHER BULLETS
            # -------------------------
            if not hasattr(bullet, "rect"):
                continue

            # Ensure bullet rect is up to date before collision detection
            bullet.update_rect()
            bullet_rect = bullet.rect

            for enemy in list(state.enemies):
                # Skip coins - they should only be collected by starship collision
                if hasattr(enemy, "__class__") and enemy.__class__.__name__ == "Coins":
                    continue

                if not bullet_rect.colliderect(enemy.hitbox):
                    continue

                enemy.enemyHealth -= getattr(bullet, "damage", 0)

                if hasattr(bullet, "trigger_explosion"):
                    bullet.trigger_explosion()
                elif getattr(bullet, "is_piercing", False):
                    pass
                else:
                    if bullet in state.player_bullets:
                        state.player_bullets.remove(bullet)

                if enemy.enemyHealth <= 0:
                    self.remove_enemy_if_dead(enemy, state)
                break
