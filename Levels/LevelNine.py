import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelNine import BossLevelNine
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.TimeBomb import TimeBomb
from Entity.Monsters.TriSpitter import TriSpitter
from SaveStates.SaveState import SaveState
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen

class LevelNine(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level9.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400
        # window_height: int = GlobalConstants.GAMEPLAY_HEIGHT
        # visible_height = window_height / self.camera.zoom
        # self.camera_y = self.WORLD_HEIGHT - visible_height
        # self.camera.world_height = self.WORLD_HEIGHT
        # self.camera_y = self.WORLD_HEIGHT - (window_height / self.camera.zoom)
        # self.camera.y = float(self.camera_y)
        self.camera.y = 80
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
        state.starship.current_level = 9

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
        super().update(state)
        # print(self.missed_enemies)
        self.update_game_over_condition()
        self.update_enemy_helper(state)
        self.update_handle_level_complete(state)
        self.update_pull_left(state)
        self.update_pull_right(state)

    def draw(self, state):
        # 1. DRAW TO scene_surface (WORLD SPACE)
        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        scene_surface = pygame.Surface((window_width, window_height))
        scene_surface.fill((20, 20, 40))

        # Base tiles
        self.draw_tiled_layers(scene_surface)
        # Unique Level Nine tiles
        self.draw_tiled_layers_leftpuller_and_rightpuller(scene_surface)

        # 2. SCALE AND BLIT TO DISPLAY (SCREEN SPACE)
        zoom = self.camera.zoom
        scaled_scene = pygame.transform.scale(
            scene_surface,
            (int(window_width * zoom), int(window_height * zoom))
        )

        state.DISPLAY.fill(GlobalConstants.BLACK)
        state.DISPLAY.blit(scaled_scene, (0, 0))


        # Player and enemies
        self.draw_player_and_enemy(state)

        # Player weapons
        self.draw_sub_weapon_rect_helper(state)

        # Enemy bullets
        for bullet in state.enemy_bullets:
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * self.camera.zoom)
            bh = int(bullet.height * self.camera.zoom)
            pygame.draw.rect(state.DISPLAY, (255, 0, 0), pygame.Rect(bx - 2, by - 2, bw + 4, bh + 4), 0)
            pygame.draw.rect(state.DISPLAY, (0, 255, 0), pygame.Rect(bx, by, bw, bh), 0)

        # UI Panel
        self.draw_ui_panel(state.DISPLAY)

        pygame.display.flip()




    def update_enemy_helper(
            self, state):
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
            enemy.__class__.__name__ == "BossLevelNine" and enemy.enemyHealth <= 0
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
            if obj.name == "level_9_boss":
                enemy = BossLevelNine()
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

    def update_pull_left(self, state) -> None:
        layer = self.tiled_map.get_layer_by_name("leftpuller")
        tile_size = self.tile_size

        # horizontal pull (pixels per frame)
        PULL_SPEED_X = 120 / 60.0

        # how much we cancel upward movement (1.0 = full cancel)
        UP_RESIST_CANCEL = 4.75

        player = self.starship
        player_rect = player.hitbox

        for col, row, image in layer.tiles():
            if image is None:
                continue

            tile_rect = pygame.Rect(
                col * tile_size,
                row * tile_size,
                tile_size,
                tile_size
            )

            if player_rect.colliderect(tile_rect):
                # pull LEFT
                player.x -= PULL_SPEED_X

                # detect upward intent by comparing hitbox movement THIS FRAME
                # (player.y was already modified earlier by input)
                dy = player.hitbox.y - player.y

                if dy != 0:
                    print("going y")

                # resist UP only (negative dy means moving up)
                if dy < 0:
                    cancel = abs(dy) * UP_RESIST_CANCEL
                    player.y += cancel  # push back DOWN slightly

                player.update_hitbox()
                break

    def update_pull_right(self, state) -> None:
        layer = self.tiled_map.get_layer_by_name("rightpuller")
        tile_size = self.tile_size

        # horizontal pull (pixels per frame)
        PULL_SPEED_X = 120 / 60.0

        # how much we cancel upward movement (same as left)
        UP_RESIST_CANCEL = 4.75

        player = self.starship
        player_rect = player.hitbox

        for col, row, image in layer.tiles():
            if image is None:
                continue

            tile_rect = pygame.Rect(
                col * tile_size,
                row * tile_size,
                tile_size,
                tile_size
            )

            if player_rect.colliderect(tile_rect):
                # pull RIGHT
                player.x += PULL_SPEED_X

                # detect upward intent (same pattern as left)
                dy = player.hitbox.y - player.y

                if dy != 0:
                    print("going y")

                # resist UP only (negative dy means moving up)
                if dy < 0:
                    cancel = abs(dy) * UP_RESIST_CANCEL
                    player.y += cancel  # push back DOWN slightly

                player.update_hitbox()
                break

    # --------------------------------------------------
    # DRAW LEFTPULLER / RIGHTPULLER TILED LAYERS
    # --------------------------------------------------


    def draw_tiled_layers_leftpuller_and_rightpuller(self, surface: pygame.Surface) -> None:
        tile_size = self.tile_size
        window_height = GlobalConstants.GAMEPLAY_HEIGHT

        for layer_name in ("leftpuller", "rightpuller"):
            layer = self.tiled_map.get_layer_by_name(layer_name)

            for col, row, image in layer.tiles():
                if image is None:
                    continue

                world_y = row * tile_size
                screen_y = world_y - self.camera.y

                if screen_y + tile_size < 0 or screen_y > window_height:
                    continue

                surface.blit(image, (col * tile_size, screen_y))
