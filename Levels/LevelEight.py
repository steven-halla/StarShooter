import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.TimeBomb import TimeBomb
from Entity.Monsters.TriSpitter import TriSpitter
from SaveStates.SaveState import SaveState
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen

class LevelEight(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level8.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400
        window_height: int = GlobalConstants.GAMEPLAY_HEIGHT
        visible_height = window_height / self.camera.zoom
        self.camera_y = self.WORLD_HEIGHT - visible_height
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - (window_height / self.camera.zoom)
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = .4  # move speed of camera
        self.total_enemies = 40
        self.prev_enemy_count: int = None
        self.enemies_killed: int = 0
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
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
        print("I only want to see this one time lleve one")
        player_x = None
        player_y = None
        state.starship.current_level = 8

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
        self.save_state.capture_player(self.starship, self.__class__.__name__)
        self.save_state.save_to_file("player_save.json")

    def update(self, state) -> None:
        super().update(state)
        # print(self.missed_enemies)
        self.update_game_over_condition()
        self.update_enemy_helper(state)
        self.update_handle_level_complete(state)


    def draw(self, state):
        super().draw(state)
        font = pygame.font.Font(None, 28)
        current_enemies = len(state.enemies)
        self.draw_player_and_enemy(state)
        self.draw_ui_panel(state.DISPLAY)

        pygame.display.flip()




    def update_enemy_helper(self, state):
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        for enemy in list(state.enemies):
            enemy.update(state)

            if enemy.y > screen_bottom:
                if enemy not in self.missed_enemies:
                    self.missed_enemies.append(enemy)
                    print("enemy missed")
                continue

            if isinstance(enemy, BileSpitter):
                enemy.is_active = True


            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)
            else:
                enemy.color = GlobalConstants.RED

            enemy.update_hitbox()

            if hasattr(enemy, "enemy_bullets") and enemy.enemy_bullets:
                state.enemy_bullets.extend(enemy.enemy_bullets)
                enemy.enemy_bullets.clear()

            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

    def update_handle_level_complete(self, state):
        if (
                not self.level_complete
                and any(
            enemy.__class__.__name__ == "BossLevelEight" and enemy.enemyHealth <= 0
            for enemy in state.enemies
        )
        ):
            self.level_complete = True
            # next_level = MissionBriefingScreenLevelNine()
            # state.currentScreen = next_level
            # next_level.start(state)



    def update_game_over_condition(self):
        if len(self.missed_enemies) > 9:
            print("GAME OVER!!!")
            self.game_over = True

    def draw_player_and_enemy(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)


    def load_enemy_into_list(self, state):
        state.enemies.clear()

        for obj in self.tiled_map.objects:
            # if obj.name == "level_8_boss":
            #     enemy = BossLevelEight()
            if obj.name == "bile_spitter":
                enemy = BileSpitter()
            elif obj.name == "time_bomb":
                enemy = TimeBomb()
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
                enemy.enemyHealth = 1  # safe fallback
            enemy.update_hitbox()

            state.enemies.append(enemy)
            print(
                f"[ADD] {enemy.__class__.__name__} "
                f"hp={enemy.enemyHealth} "
                f"→ enemies size = {len(state.enemies)}"
            )
