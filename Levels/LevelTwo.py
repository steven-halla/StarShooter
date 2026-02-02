import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelTwo import BossLevelTwo
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher

from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.TriSpitter import TriSpitter
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen
from ShipEngine.Shield import Shield

class LevelTwo(VerticalBattleScreen):
    def __init__(self, textbox):
        super().__init__(textbox)
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level2.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400
        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - window_height
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = 0.4
        self.prev_enemy_count: int = None
        self.enemies_killed: int = 0
        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.level_complete = False
        self.side_rect_width = 16
        self.side_rect_height = 16
        self.side_rect_shield = Shield(100, 0.05, 3000)
        self.side_rect_shield.owner = self
        self.shipHealth = 100 # for shield overflow
        self.side_rect_hitbox = pygame.Rect(0, 0, 0, 0)
        self.game_over: bool = False

    def start(self, state) -> None:
        print("LEVEL 2 I wanna see this one time")
        player_x = None
        player_y = None
        state.starship.current_level = 2
        self.starship = state.starship

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break
        if "Metal Shield" not in state.starship.magic_inventory:
            state.starship.magic_inventory.append("Metal Shield")
        state.starship.equipped_magic = ["Metal Shield", None]
        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list(state)
        self.save_state.capture_player(self.starship)
        self.save_state.save_to_file("player_save.json")


    def update(self, state) -> None:
        super().update(state)
        self.side_rect_shield.update()
        self.update_side_ship()
        self.update_enemy_helper(state)
        self.update_complete_level(state)

    def draw(self, state):
        super().draw(state)
        zoom = self.camera.zoom
        self.draw_player_and_enemies(state)
        self.draw_side_ship_rectangle_life_meter(state, zoom)
        self.draw_ui_panel(state.DISPLAY)
        pygame.display.flip()


    def update_complete_level(self,state):
        if (
                not self.level_complete
                and any(
            enemy.__class__.__name__ == "BossLevelTwo" and enemy.enemyHealth <= 0
            for enemy in state.enemies
        )
        ):
            self.level_complete = True
            return


    def update_side_ship(self):
        side_x = self.starship.x + self.starship.width + 10
        side_y = self.starship.y + (self.starship.height // 2) - (self.side_rect_height // 2)
        self.side_rect_hitbox.update(
            int(side_x),
            int(side_y),
            self.side_rect_width,
            self.side_rect_height
        )
        hazard_layer = self.tiled_map.get_layer_by_name("hazard")
        if self.side_rect_shield.current_shield_points > 0:
            for x, y, gid in hazard_layer:
                if gid == 0:
                    continue

                tile_rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )

                if self.side_rect_hitbox.colliderect(tile_rect):
                    self.side_rect_shield.take_damage(1)
                    print("⚠️ Side rect took hazard damage:", self.side_rect_shield.current_shield_points)
                    break

    def update_enemy_helper(self, state):
        now = pygame.time.get_ticks()

        dead_enemies = []

        # SIDE RECT vs ENEMIES
        for enemy in state.enemies:
            if enemy.hitbox.colliderect(self.side_rect_hitbox):
                self.side_rect_shield.take_damage(10)
                print("⚠️ SIDE RECT TOOK CONTACT DAMAGE:", self.side_rect_shield.current_shield_points)

        # SIDE RECT vs ENEMY BULLETS
        for bullet in list(state.enemy_bullets):
            bullet_rect = pygame.Rect(
                bullet.x,
                bullet.y,
                bullet.width,
                bullet.height
            )

            if bullet_rect.colliderect(self.side_rect_hitbox):
                self.side_rect_shield.take_damage(bullet.damage)
                print("⚠️ SIDE RECT HIT:", self.side_rect_shield.current_shield_points)

                state.enemy_bullets.remove(bullet)

        # ENEMY UPDATE
        for enemy in state.enemies:
            enemy.update(state)

            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)
            else:
                enemy.color = GlobalConstants.RED

            enemy.update_hitbox()

            if enemy.enemyHealth <= 0:
                dead_enemies.append(enemy)

        # SAFE CLEANUP (AFTER ALL UPDATES)
        for enemy in dead_enemies:
            state.enemies.remove(enemy)



    def draw_player_and_enemies(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

    def draw_side_ship_rectangle_life_meter(self, state, zoom):
        side_screen_x = self.camera.world_to_screen_x(self.side_rect_hitbox.x)
        side_screen_y = self.camera.world_to_screen_y(self.side_rect_hitbox.y)
        side_w = int(self.side_rect_hitbox.width * zoom)
        side_h = int(self.side_rect_hitbox.height * zoom)
        hp_ratio = max(0, self.side_rect_shield.current_shield_points / self.side_rect_shield.max_shield_points)
        hp_width = int(side_w * hp_ratio)
        # background
        pygame.draw.rect(
            state.DISPLAY,
            (60, 60, 60),
            (side_screen_x, side_screen_y, side_w, side_h)
        )
        # HP fill
        pygame.draw.rect(
            state.DISPLAY,
            (0, 255, 0),
            (side_screen_x, side_screen_y, hp_width, side_h)
        )
        # outline
        pygame.draw.rect(
            state.DISPLAY,
            (255, 255, 255),
            (side_screen_x, side_screen_y, side_w, side_h),
            1
        )
        if self.shipHealth < 100:
             # Just an example of what to do if it's "destroyed" (overflow damage taken)
             pass

    def load_enemy_into_list(self, state):
        state.enemies.clear()
        # print("[LOAD] clearing enemies list")

        for obj in self.tiled_map.objects:
            enemy = None

            print(f"[TMX] found object name={obj.name} at ({obj.x}, {obj.y})")

            if obj.name == "level_2_boss":
                enemy = BossLevelTwo()
            elif obj.name == "bile_spitter":
                enemy = BileSpitter()
            elif obj.name == "blade_spinner":
                enemy = BladeSpinner()
            elif obj.name == "tri_spitter":
                enemy = TriSpitter()
            elif obj.name == "fire_launcher":
                enemy = FireLauncher()
            else:
                continue

            # position / size
            enemy.x = obj.x
            enemy.y = obj.y
            enemy.width = obj.width
            enemy.height = obj.height

            # REQUIRED state
            enemy.camera = self.camera
            enemy.target_player = self.starship



            enemy.update_hitbox()

            state.enemies.append(enemy)
            print(
                f"[ADD] {enemy.__class__.__name__} "
                f"hp={enemy.enemyHealth} "
                f"→ enemies size = {len(state.enemies)}"
            )

        print(f"[DONE] total enemies loaded = {len(state.enemies)}")
# enemy name:  count
# Bile spitter: 10
# fire launcehr: 12
# tri spitter: 10
# blade spinner: 12
