import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Bosses.BossLevelTen import BossLevelTen
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.ObjectiveBlock import ObjectiveBlock
from Entity.Monsters.ShootingUpBlock import ShootingUpBlock
from Entity.Monsters.TriSpitter import TriSpitter
from SaveStates.SaveState import SaveState
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen

###
# Spiky boys can protect worms, use side shot to kill them faster.
# we can implement a new enemy type that shoots UP when it's hit.
# Use PLASMA BLASTER to shoot through narrow passages and to power it pu
###
class LevelTen(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level10.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400
        window_height: int = GlobalConstants.GAMEPLAY_HEIGHT
        visible_height = window_height / self.camera.zoom
        # self.camera_y = self.WORLD_HEIGHT - visible_height
        # self.camera.world_height = self.WORLD_HEIGHT
        # self.camera_y = self.WORLD_HEIGHT - (window_height / self.camera.zoom)
        # self.camera.y = float(self.camera_y)
        self.camera.y = 80
        self.map_scroll_speed_per_frame: float = .4  # move speed of camera
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
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
        print("I only want to see this one time lleve one")
        player_x = None
        player_y = None
        state.starship.current_level = 10

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break
        self.starship = state.starship
        self.starship.x = player_x
        self.starship.y = player_y

        self.load_enemy_into_list(state)
        self.starship.shipHealth = 144
        self.save_state.capture_player(self.starship)
        self.save_state.save_to_file("player_save.json")

    def update(self, state) -> None:
        # Create melee_hitbox FIRST (before enemies update)
        self.starship.melee_hitbox = pygame.Rect(
            int(self.starship.x),
            int(self.starship.y),
            self.starship.width,
            self.starship.height
        )

        super().update(state)

        self.update_game_over_condition()
        self.update_enemy_helper(state)
        self.update_handle_level_complete(state)
        self.update_collision_tiles(state, damage=5)


    def draw(self, state):
        super().draw(state)
        # self.draw_level_collision(state.DISPLAY)

        self.draw_player_and_enemy(state)
        self.draw_ui_panel(state.DISPLAY)

        pygame.display.flip()

    # LevelTen.update_enemy_helper
    def draw_level_collision(self, surface: pygame.Surface) -> None:
        self.draw_collision_tiles(surface)

    def update_enemy_helper(self, state):
        screen_top = self.camera.y
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        # default: scrolling ON
        self.map_scroll_speed_per_frame = 0.4

        for enemy in list(state.enemies):
            # update ALL enemies once
            enemy.update(state)
            enemy.update_hitbox()

            # ONLY ObjectiveBlock can lock scroll
            if enemy.name == "ObjectiveBlock":
                enemy_fully_on_screen = (
                        enemy.y >= screen_top
                        and enemy.y + enemy.height <= screen_bottom
                )

                player = self.starship
                player_fully_on_screen = (
                        player.y >= screen_top
                        and player.y + player.height <= screen_bottom
                )

                if enemy_fully_on_screen and player_fully_on_screen:
                    self.map_scroll_speed_per_frame = 0
                    self.camera.y = self.camera.y

            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

    def update_handle_level_complete(self, state):

        pass


    def update_game_over_condition(self):
        pass

    def draw_player_and_enemy(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)


    def load_enemy_into_list(self, state):
        state.enemies.clear()

        for obj in self.tiled_map.objects:
            if obj.name == "level_10_boss":
                enemy = BossLevelTen()
            elif obj.name == "bile_spitter":
                enemy = BileSpitter()
            elif obj.name == "shooting_up_block":
                enemy = ShootingUpBlock()
            elif obj.name == "objective_block":
                enemy = ObjectiveBlock()

            else:
                continue

            enemy.x = obj.x
            enemy.y = obj.y
            enemy.width = obj.width
            enemy.height = obj.height

            enemy.camera = self.camera
            enemy.target_player = self.starship


            enemy.update_hitbox()

            state.enemies.append(enemy)
            print(
                f"[ADD] {enemy.__class__.__name__} "
                f"hp={enemy.enemyHealth} "
                f"→ enemies size = {len(state.enemies)}"
            )

    # 🔑 THE Y-CLAMP IS NOT HERE
    # It is coming from Enemy.update() → clamp_vertical()

    # ===============================
    # FIX: DISABLE Y CLAMP FOR THIS ENEMY
    # ===============================

