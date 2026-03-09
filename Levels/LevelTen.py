import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Bosses.BossLevelTen import BossLevelTen
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.ObjectiveBlock import ObjectiveBlock
from Entity.Monsters.ShootingUpBlock import ShootingUpBlock
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.SporeFlower import SporeFlower
from Entity.Monsters.TriSpitter import TriSpitter
from Entity.Monsters.WaspStinger import WaspStinger
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
        # self.camera.y = 80
        self.map_scroll_speed_per_frame: float = .4  # move speed of camera
        self.time_limit_ms = 5 * 60 * 1000  # 5 minutes
        self.start_ticks = 0
        self.game_over: bool = False
        self.level_complete = False
        self.save_state = SaveState()
        self.pending_enemies = []

        self.intro_dialogue = (
            "I am the ultimate man on the battlefield. "
            "You cannot hope to win against the likes of me. "
            "Prepare yourself, dum dum mortal head. "
            "Bla bla bla bla bla. "
            "Win against the likes of me if you dare."
        )

    def start(self, state) -> None:
        print("I only want to see this one time lleve one")
        self.start_ticks = pygame.time.get_ticks()
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
        self.save_state.set_location_level(10, screen_name="Level 10")
        self.save_state.capture_player(self.starship)
        self.save_state.save_to_file("player_save.json")

    def update(self, state) -> None:
        # Create melee_hitbox FIRST (before enemies update)
        # print(len(state.enemies))
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
        self.draw_timer(state.DISPLAY)

        pygame.display.flip()

    def draw_timer(self, surface: pygame.Surface) -> None:
        elapsed_time = pygame.time.get_ticks() - self.start_ticks
        remaining_time = max(0, self.time_limit_ms - elapsed_time)

        minutes = (remaining_time // 1000) // 60
        seconds = (remaining_time // 1000) % 60

        timer_text = f"{minutes:02}:{seconds:02}"
        font = pygame.font.Font(None, 36)
        text_surface = font.render(timer_text, True, (255, 255, 255))

        # Position at top right
        text_rect = text_surface.get_rect()
        text_rect.topright = (GlobalConstants.BASE_WINDOW_WIDTH - 20, 20)

        # Draw a small semi-transparent background for readability
        bg_rect = text_rect.inflate(10, 10)
        pygame.draw.rect(surface, (0, 0, 0, 128), bg_rect)
        surface.blit(text_surface, text_rect)

    # LevelTen.update_enemy_helper
    def draw_level_collision(self, surface: pygame.Surface) -> None:
        self.draw_collision_tiles(surface)

    def update_enemy_helper(self, state):
        screen_top = self.camera.y
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        # ----------------------------------------------------------------------
        # Lazy Loading: Move enemies from pending_enemies to state.enemies
        # if they are within 50px above the screen's top edge.
        # ----------------------------------------------------------------------
        for enemy in list(self.pending_enemies):
            # Load Zone: y >= camera.y - 50
            if enemy.y >= self.camera.y - 50:
                state.enemies.append(enemy)
                self.pending_enemies.remove(enemy)
                print(f"[LAZY LOAD] {enemy.__class__.__name__} at y={enemy.y}")

        # default: scrolling ON
        self.map_scroll_speed_per_frame = 0.4

        for b in list(state.enemy_bullets):
            if getattr(b, "is_acid_missile", False) and getattr(b, "is_tracking", False):
                if self.starship:
                    px = self.starship.hitbox.centerx
                    py = self.starship.hitbox.centery
                    dx = px - (b.x + b.width / 2)
                    dy = py - (b.y + b.height / 2)
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist != 0:
                        b.vx = dx / dist
                        b.vy = dy / dist

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
                self.remove_enemy_if_dead(enemy, state)

    def remove_enemy_if_dead(self, enemy, state) -> None:
        if enemy.enemyHealth <= 0 and isinstance(enemy, ObjectiveBlock):
            self.time_limit_ms += 60000
        super().remove_enemy_if_dead(enemy, state)

    def update_handle_level_complete(self, state):

        pass


    def update_game_over_condition(self):
        elapsed_time = pygame.time.get_ticks() - self.start_ticks
        if elapsed_time >= self.time_limit_ms:
            self.game_over = True
            # Assuming there is a way to handle game over in the parent or game loop
            # For now just setting the flag.
            # In many of these screens, game_over=True might trigger a reload or title screen.
            self.starship.shipHealth = 0 # Trigger death if time runs out

    def draw_player_and_enemy(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        # Draw damage flash for acid missiles
        for b in state.enemy_bullets:
            if getattr(b, "is_acid_missile", False) and getattr(b, "is_flashing", False):
                elapsed = pygame.time.get_ticks() - b.flash_start_time
                if elapsed < b.flash_duration_ms:
                    if (elapsed // b.flash_interval_ms) % 2 == 0:
                        x = self.camera.world_to_screen_x(b.x)
                        y = self.camera.world_to_screen_y(b.y)
                        w = int(b.width * self.camera.zoom)
                        h = int(b.height * self.camera.zoom)

                        flash = pygame.Surface((w, h), pygame.SRCALPHA)
                        flash.fill((*GlobalConstants.RED, 160))
                        state.DISPLAY.blit(flash, (x, y))
                else:
                    b.is_flashing = False


    def load_enemy_into_list(self, state):
        state.enemies.clear()
        self.pending_enemies.clear()

        for obj in self.tiled_map.objects:
            if obj.name == "level_10_boss":
                enemy = BossLevelTen()
            elif obj.name == "spine_launcher":
                enemy = SpineLauncher()
            elif obj.name == "spore_flower":
                enemy = SporeFlower()
            elif obj.name == "tri_spitter":
                enemy = TriSpitter()
            elif obj.name == "blade_spinner":
                enemy = BladeSpinner()
            elif obj.name == "wasp_stinger":
                enemy = WaspStinger()
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

            self.pending_enemies.append(enemy)
            print(
                f"[PENDING] {enemy.__class__.__name__} "
                f"hp={enemy.enemyHealth} "
                f"→ pending size = {len(self.pending_enemies)}"
            )

    # 🔑 THE Y-CLAMP IS NOT HERE
    # It is coming from Enemy.update() → clamp_vertical()

    # ===============================
    # FIX: DISABLE Y CLAMP FOR THIS ENEMY
    # ===============================

