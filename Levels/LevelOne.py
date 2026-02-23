import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.TriSpitter import TriSpitter
from SaveStates.SaveState import SaveState
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen

class LevelOne(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level1.tmx")
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
        self.total_enemies = 40
        self.prev_enemy_count: int = None

        self.enemies_killed: int = 0
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.missed_enemies: list[int] = []
        self.game_over: bool = False
        self.level_complete:bool = False
        self.save_state = SaveState()
        self.map_scroll_speed_per_frame: float = .4


        self.intro_dialogue = (
            "I am the ultimate man on the battlefield. "
            "You cannot hope to win against the likes of me. "
            "Prepare yourself, dum dum mortal head. "
            "Bla bla bla bla bla. "
            "Win against the likes of me if you dare."
        )

    def start(self, state) -> None:
        print("I only want to see this one time lleve one")
        state.starship.equipped_magic = ["", None]
        state.starship.current_level = 1
        player_x = None

        player_y = None

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break
        self.starship = state.starship
        self.starship.x = player_x
        self.starship.y = player_y

        self.load_enemy_into_list(state)
        self.save_state.set_location_level(1, screen_name="Level 1")
        self.save_state.capture_player(self.starship)
        self.save_state.save_to_file("player_save.json")
        state.starship.apply_upgrades()


    def update(self, state) -> None:
        super().update(state)
        print(self.missed_enemies)
        if self.missed_enemies.__len__() > 3:
            print("Objective failed!!!")
        # print(f"Player X: {self.starship.x}, Player Y: {self.starship.y}, Camera Y: {self.camera.y}")
        # print(self.missed_enemies)
        if not hasattr(self, "last_enemy_count"):
            self.last_enemy_count = len(state.enemies)

        self.last_enemy_count = len(state.enemies)
        self.update_game_over_condition()
        self.update_add_enemy_to_missed_list(state)
        self.update_enemy_helper(state)
        self.update_handle_level_complete(state)

    def draw(self, state):
        super().draw(state)
        font = pygame.font.Font(None, 28)
        current_enemies = len(state.enemies)
        self.draw_enemy_counter(current_enemies, font, state)
        self.draw_player_and_enemy(state)
        self.draw_ui_panel(state.DISPLAY)

        pygame.display.flip()


    def update_enemy_helper(self, state):
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        for enemy in list(state.enemies):

            if enemy.y > screen_bottom:
                if enemy not in self.missed_enemies:
                    self.missed_enemies.append(enemy)
                    print("enemy missed")
                continue


            enemy.update(state)


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
            enemy.__class__.__name__ == "BossLevelOne" and enemy.enemyHealth <= 0
            for enemy in state.enemies
        )
        ):
            self.level_complete = True
            next_level = MissionBriefingScreenLevelTwo()
            state.currentScreen = next_level
            next_level.start(state)

    def update_add_enemy_to_missed_list(self, state):
        UI_KILL_PADDING = 13.5  # pixels ABOVE the UI panel (tweak this)
        screen_bottom = (
                self.camera.y
                + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)
                - UI_KILL_PADDING
        )
        for enemy in list(state.enemies):
            if enemy.y > screen_bottom:
                if enemy not in self.missed_enemies:
                    self.missed_enemies.append(enemy)
                    print(self.missed_enemies)
                    if self.missed_enemies.__len__() > 3:
                        print("GAME OVER!!!")

    def update_game_over_condition(self):
        if len(self.missed_enemies) > 3:
            print("GAME OVER!!!")
            self.game_over = True

    def draw_player_and_enemy(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

    def draw_enemy_counter(self, current_enemies, font, state):
        now = pygame.time.get_ticks()

        # ---------------------------------
        # lazy-init local state (ONCE)
        # ---------------------------------
        if not hasattr(self, "_counter_pending_kill_delta"):
            self._counter_pending_kill_delta = 0
            self._counter_delay_start = None

        COUNTER_DELAY_MS = 250

        # ---------------------------------
        # detect enemy count change
        # ---------------------------------
        if self.prev_enemy_count is None:
            self.prev_enemy_count = current_enemies
        else:
            delta = self.prev_enemy_count - current_enemies

            if delta > 0:
                self._counter_pending_kill_delta += delta
                self._counter_delay_start = now

            self.prev_enemy_count = current_enemies

        # ---------------------------------
        # apply delayed update
        # ---------------------------------
        if (
                self._counter_delay_start is not None
                and now - self._counter_delay_start >= COUNTER_DELAY_MS
        ):
            self.enemies_killed += self._counter_pending_kill_delta
            self._counter_pending_kill_delta = 0
            self._counter_delay_start = None

        # ---------------------------------
        # draw (no flicker)
        # ---------------------------------
        if len(self.missed_enemies) > 3:
            enemy_text = font.render(
                "objective failed",
                True,
                (255, 0, 0)
            )
        else:
            enemy_text = font.render(
                f"enemies missed {len(self.missed_enemies)} / 4",
                True,
                (255, 255, 255)
            )
        state.DISPLAY.blit(enemy_text, (10, 50))

    # def draw_enemy_counter(self, current_enemies, font, state):
    #     if self.prev_enemy_count is None:
    #         self.prev_enemy_count = current_enemies
    #     else:
    #         if current_enemies < self.prev_enemy_count:
    #             self.enemies_killed += (self.prev_enemy_count - current_enemies)
    #
    #         self.prev_enemy_count = current_enemies
    #     enemy_text = font.render(
    #         f"Enemies {self.enemies_killed - len(self.missed_enemies)}/40",
    #         True,
    #         (255, 255, 255)
    #     )
    #     state.DISPLAY.blit(enemy_text, (10, 50))

    def load_enemy_into_list(self, state):
        state.enemies.clear()

        for obj in self.tiled_map.objects:
            if obj.name == "level_1_boss":
                enemy = BossLevelOne()
            elif obj.name == "bile_spitter":
                enemy = BileSpitter()
            elif obj.name == "blade_spinner":
                enemy = BladeSpinner()
            elif obj.name == "tri_spitter":
                enemy = TriSpitter()
            else:
                continue

            enemy.x = obj.x
            enemy.y = obj.y
            enemy.width = obj.width
            enemy.height = obj.height

            enemy.camera = self.camera
            enemy.target_player = self.starship

            # 🔑 CRITICAL FIX: ensure health is initialized

            enemy.update_hitbox()

            state.enemies.append(enemy)
            # print(
            #     f"[ADD] {enemy.__class__.__name__} "
            #     f"hp={enemy.enemyHealth} "
            #     f"→ enemies size = {len(state.enemies)}"
            # )
