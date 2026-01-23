import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelTwo import BossLevelTwo
from Entity.Monsters.BileSpitter import BileSpitter

from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.TriSpitter import TriSpitter
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen

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
        self.map_scroll_speed_per_frame: float = .4
        self.prev_enemy_count: int = None
        self.enemies_killed: int = 0
        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.level_complete = False
        self.side_rect_width = 16
        self.side_rect_height = 16
        self.side_rect_hp = 50
        self.side_rect_max_hp = 50
        self.side_rect_hitbox = pygame.Rect(0, 0, 0, 0)
        self.game_over: bool = False

    def start(self, state) -> None:
        player_x = None
        player_y = None
        self.starship.shipHealth = 333

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list(state)

        self.save_state.capture_player(self.starship, self.__class__.__name__)
        self.save_state.save_to_file("player_save.json")

    def update(self, state) -> None:
        super().update(state)
        self.update_side_rect_invincibility()

        side_x = self.starship.x + self.starship.width + 10
        side_y = self.starship.y + (self.starship.height // 2) - (self.side_rect_height // 2)

        self.side_rect_hitbox.update(
            int(side_x),
            int(side_y),
            self.side_rect_width,
            self.side_rect_height
        )

        hazard_layer = self.tiled_map.get_layer_by_name("hazard")

        if self.side_rect_hp > 0 and not self.side_rect_invincible:
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
                    self.side_rect_hp -= 1
                    self.side_rect_invincible = True
                    self.side_rect_invincible_start_time = pygame.time.get_ticks()
                    print("⚠️ Side rect took hazard damage:", self.side_rect_hp)
                    break

        self.enemy_helper(state)
        if (
                not self.level_complete
                and any(
            enemy.__class__.__name__ == "BossLevelTwo" and enemy.enemyHealth <= 0
            for enemy in state.enemies
        )
        ):
            self.level_complete = True
            return

    def draw(self, state):
        super().draw(state)

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

        # -------------------------
        # SIDE RECT HP BAR (ONLY HP BAR)
        # -------------------------
        side_screen_x = self.camera.world_to_screen_x(self.side_rect_hitbox.x)
        side_screen_y = self.camera.world_to_screen_y(self.side_rect_hitbox.y)

        side_w = int(self.side_rect_hitbox.width * zoom)
        side_h = int(self.side_rect_hitbox.height * zoom)

        hp_ratio = max(0, self.side_rect_hp / self.side_rect_max_hp)
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

        self.draw_ui_panel(state.DISPLAY)

        pygame.display.flip()

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

            if obj.name == "level_2_boss":
                enemy = BossLevelTwo()
            elif obj.name == "bile_spitter":
                enemy = BileSpitter()
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
        now = pygame.time.get_ticks()

        for enemy in list(state.enemies):

            if enemy.hitbox.colliderect(self.side_rect_hitbox):

                if not self.side_rect_invincible:
                    self.side_rect_hp -= 10
                    self.side_rect_invincible = True
                    self.side_rect_invincible_start_time = pygame.time.get_ticks()
                    print("⚠️ SIDE RECT TOOK CONTACT DAMAGE:", self.side_rect_hp)

        for bullet in list(state.enemy_bullets):

            # bullet rect in WORLD space
            bullet_rect = pygame.Rect(
                bullet.x,
                bullet.y,
                bullet.width,
                bullet.height
            )

            # SIDE RECT TAKES PRIORITY
            if bullet_rect.colliderect(self.side_rect_hitbox):

                if not self.side_rect_invincible:
                    self.side_rect_hp -= bullet.damage
                    self.side_rect_invincible = True
                    self.side_rect_invincible_start_time = now
                    print("⚠️ SIDE RECT HIT:", self.side_rect_hp)

                # bullet is ALWAYS destroyed
                state.enemy_bullets.remove(bullet)
                continue
        for enemy in list(state.enemies):

            # update enemy
            enemy.update(state)
            # enemy.update_hitbox()

            # color change on player collision (same logic as before)
            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)
            else:
                enemy.color = GlobalConstants.RED

            enemy.update_hitbox()

            # emit enemy bullets (same behavior as before)
            if state.enemy_bullets:
                state.enemy_bullets.extend(state.enemy_bullets)
                state.enemy_bullets.clear()

            # death removal
            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

    # SIDE RECT INVINCIBILITY TIMER (NO DAMAGE LOGIC HERE)
    # =========================
    def update_side_rect_invincibility(self) -> None:
        if not hasattr(self, "side_rect_invincible"):
            self.side_rect_invincible = False
            self.side_rect_invincible_start_time = 0
            return

        if self.side_rect_invincible:
            if pygame.time.get_ticks() - self.side_rect_invincible_start_time >= 1000:
                self.side_rect_invincible = False
