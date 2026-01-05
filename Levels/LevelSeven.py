import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Bosses.BossLevelSeven import BossLevelSeven
from Entity.Enemy import Enemy
from Entity.Monsters.AcidLauncher import AcidLauncher
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.Ravager import Ravager
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.SporeFlower import SporeFlower
from Entity.Monsters.TriSpitter import TriSpitter
from SaveStates.SaveState import SaveState
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen
from Weapons.Weapon import Weapon

UI_HEIGHT = 0
BULLET_SIZE = 64
NUM_BULLETS = 10
BULLET_DAMAGE = 30


class LevelSeven(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        # self.starship: StarShip = StarShip()

        self.bossLevelSevenGroup: list[BossLevelSeven] = []
        self.level_start:bool = True
        self.current_page_lines: list[list[str]] = []
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level7.tmx")
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

        # self.enemies: list[Enemy] = [] # consolidate all enemies into one list
        # self.load_enemy_into_list()
        self.napalm_list: list = []
        self.total_enemies = 40
        self.prev_enemy_count: int = None
        self.enemies_killed: int = 0

        self.level_start_time = pygame.time.get_ticks()

        self.game_over: bool = False
        self.level_complete = False
        self.save_state = SaveState()
        self.bullet_damage = 10
        self.bullet_size = 64
        self.bullet_y_offset = 50

        # self.intro_dialogue = (
        #     "I am the ultimate man on the battlefield. "
        #     "You cannot hope to win against the likes of me. "
        #     "Prepare yourself, dum dum mortal head. "
        #     "Bla bla bla bla bla. "
        #     "Win against the likes of me if you dare."
        # )

    from Weapons.Weapon import Weapon

    def create_static_bottom_bullets(self, screen_width: int, screen_height: int):
        bullets = []

        spacing = screen_width // NUM_BULLETS
        y = screen_height - UI_HEIGHT - BULLET_SIZE

        for i in range(NUM_BULLETS):
            x = i * spacing + (spacing - BULLET_SIZE) // 2
            bullet = Weapon(x, y)
            bullet.width = BULLET_SIZE
            bullet.height = BULLET_SIZE
            bullet.update_rect()
            bullets.append(bullet)

        return bullets

    def clear_all_enemy_groups(self) -> None:
        self.bileSpitterGroup.clear()
        self.kamikazeDroneGroup.clear()
        self.triSpitterGroup.clear()
        self.waspStingerGroup.clear()
        self.bladeSpinnerGroup.clear()
        self.sporeFlowerGroup.clear()
        self.spineLauncherGroup.clear()
        self.acidLauncherGroup.clear()
        self.ravagerGroup.clear()
        self.fireLauncherGroup.clear()
        self.transportWormGroup.clear()
        self.spinalRaptorGroup.clear()
        self.slaverGroup.clear()
        self.coinsGroup.clear()
        self.spikeyBallGroup.clear()



    def start(self, state) -> None:
        player_x = None
        # self.textbox.show(self.intro_dialogue)
        player_y = None

        self.static_bullets = self.create_static_bottom_bullets(
            GlobalConstants.BASE_WINDOW_WIDTH,
            GlobalConstants.GAMEPLAY_HEIGHT
        )

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break
        self.starship = state.starship

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()
        # self.starship.x = player_x
        # self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list()

    def move_map_y_axis(self):
        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = GlobalConstants.GAMEPLAY_HEIGHT

        # move camera UP in world space (so map scrolls down)
        self.camera_y -= self.map_scroll_speed_per_frame * 1.5

        # clamp so we never scroll past top or bottom of the map
        max_camera_y = self.WORLD_HEIGHT - window_height
        if max_camera_y < 0:
            max_camera_y = 0

        if self.camera_y < 0:
            self.camera_y = 0
        elif self.camera_y > max_camera_y:
            self.camera_y = max_camera_y

        # keep Camera object in sync
        self.camera.y = float(self.camera_y)


    def update(self, state) -> None:
        super().update(state)
        self.update_static_bullets(self.static_bullets, self.starship.hitbox)
        # print("=== ENEMY LIST ===")
        # print(f"BileSpitter: {len(self.bileSpitterGroup)}")
        # print(f"TriSpitter: {len(self.triSpitterGroup)}")
        # print(f"BladeSpinner: {len(self.bladeSpinnerGroup)}")
        # print(f"BossLevelOne: {len(self.bossLevelOneGroup)}")
        # print(
        #     f"TOTAL: "
        #     f"{len(self.bileSpitterGroup) + len(self.triSpitterGroup) + len(self.bladeSpinnerGroup) + len(self.bossLevelOneGroup)}"
        # )
        # print("==================")
        # if len(self.missed_enemies) > 9:
        #     print("GAME OVER!!!")
        #     self.game_over = True

        if self.level_start == True:
            self.level_start = False
            self.starship.shipHealth = 244
            self.clear_all_enemy_groups()
            self.save_state.capture_player(self.starship, self.__class__.__name__)
            self.save_state.save_to_file("player_save.json")



        now = pygame.time.get_ticks()
        elapsed = now - self.level_start_time

        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)



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
        # if not self.bossLevelSevenGroup and not self.level_complete:
        #     self.level_complete = True


        self.extract_object_names()
        # if self.level_complete:
        #
        #     next_level = MissionBriefingScreenLevelTwo()
        #     # next_level.set_player(state.starship)
        #     state.currentScreen = next_level
        #     next_level.start(state)
        #     print(type(state.currentScreen).__name__)
        #
        #     return

        self.move_map_y_axis()

        self.update_collision_tiles(damage=5)


        self.repeat_map()

    def draw_level_collision(self, surface: pygame.Surface) -> None:
        self.draw_collision_tiles(surface)

    def draw(self, state):
        super().draw(state)
        # ================================
        # ENEMY COUNTER (TOP OF SCREEN)
        # ================================
        font = pygame.font.Font(None, 28)

        current_enemies = (

                + len(self.bossLevelSevenGroup)
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

        # for obj in self.tiled_map.objects:
        #     if hasattr(obj, "image") and obj.image is not None:
        #         screen_x = self.camera.world_to_screen_x(obj.x)
        #         screen_y = self.camera.world_to_screen_y(obj.y)
        #         state.DISPLAY.blit(obj.image, (screen_x, screen_y))

        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)


        for boss in self.bossLevelSevenGroup:
            boss.draw(state.DISPLAY, self.camera)
            boss.draw_damage_flash(state.DISPLAY, self.camera)

        self.draw_static_bullets(self.static_bullets, state.DISPLAY)

        self.draw_ui_panel(state.DISPLAY)
        # self.textbox.show("I am the ultimate man on the battlefiled. You cannot hope to win aginst the likes of me, prepare yourself dum dum mortal head. bla bla bal bal bla; win  the likes of me, prepare yourself dum dum mortal head. bla bla bal bal bla")

        # self.textbox.draw(state.DISPLAY)

        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        enemies = (
                list(self.bossLevelSevenGroup)
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

        self.bossLevelSevenGroup.clear()
        for obj in self.tiled_map.objects:
            # ⭐ LOAD ENEMIES (existing code)
            if obj.name == "level_7_boss":
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
        for boss in list(self.bossLevelSevenGroup):


            boss.update()

            if boss.enemyBullets:
                self.enemy_bullets.extend(boss.enemyBullets)
                boss.enemyBullets.clear()

            if boss.enemyHealth <= 0:
                self.bossLevelSevenGroup.remove(boss)
                print("level complete")

    def repeat_map(self) -> None:
        """
        Seamlessly wrap the map vertically when the camera reaches the top,
        keeping player motion smooth (no snap / no visible jump).
        """

        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        map_height = self.map_height_tiles * self.tile_size

        # when camera scrolls past the top, wrap
        if self.camera.y <= 0:
            wrap_offset = map_height

            # shift camera down by one full map height
            self.camera.y += wrap_offset
            self.camera_y = self.camera.y

            # shift player down by same amount (preserves relative position)
            self.starship.y += wrap_offset
            self.starship.update_hitbox()

            # shift all world entities down
            for group in (
                    self.coinsGroup,
                    self.spikeyBallGroup,
                    self.bossLevelSixGroup,
            ):
                for enemy in group:
                    enemy.y += wrap_offset
                    enemy.update_hitbox()

                    # Static bottom bullets using Weapon

    def update_static_bullets(self, bullets: list[Weapon], player_hitbox: pygame.Rect) -> None:

        player_screen_rect = pygame.Rect(
            self.camera.world_to_screen_x(player_hitbox.x),
            self.camera.world_to_screen_y(player_hitbox.y),
            player_hitbox.width,
            player_hitbox.height
        )

        for bullet in bullets:
            if bullet.rect.colliderect(player_screen_rect):
                self.starship.shipHealth -= BULLET_DAMAGE
                print("Player bullet collision")

    def draw_static_bullets(
            self,
            bullets: list[Weapon],
            surface: pygame.Surface
    ) -> None:
        for bullet in bullets:
            bullet.draw(surface)
