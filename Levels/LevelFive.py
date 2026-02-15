import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelFive import BossLevelFive
from Entity.Monsters.AcidLauncher import AcidLauncher
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.Ravager import Ravager
from Entity.Monsters.RescuePod import RescuePod
from Entity.Monsters.SpinalRaptor import SpinalRaptor
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.WaspStinger import WaspStinger
from SaveStates.SaveState import SaveState
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen

class LevelFive(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        self.level_start:bool = True
        self.current_page_lines: list[list[str]] = []
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level5.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400 # y position of map
        window_height: int = GlobalConstants.GAMEPLAY_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - window_height # look at bottom of map
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.rescue_pods = []
        self.rescue_pod_destroyed = 0
        self.flame_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.game_over: bool = False
        self.level_complete = False
        self.save_state = SaveState()
        self.hazard_active = False
        self.hazard_start_time = None
        self.fire_last_growth_time = None
        self.fire_row_index = 0
        self.fire_rows_completed = 0
        self.fire_row_length = 0
        self.MAX_FIRE_ROW_LENGTH = 27
        self.MAX_FIRE_ROWS = 20

    def start(self, state) -> None:
        player_x = None
        player_y = None
        state.starship.current_level = 5

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
        self.save_state.capture_player(self.starship)
        self.save_state.save_to_file("player_save.json")

    def update(self, state) -> None:
        super().update(state)
        self.update_enemy_helper(state)
        self.update_rescue_pod_helper(state)
        self.update_hazard_square(state,current_time_ms=500)
        self.update_hazard_damage(state.DISPLAY.get_height())

    def draw(self, state):
        super().draw(state)
        self.draw_player_and_enemy(state)
        self.draw_hazard_square(state.DISPLAY, self.camera)
        pygame.display.flip()

    def update_hazard_square(self,state, current_time_ms: int) -> None:
        if not self.is_boss_on_screen(state):
            return

        if not self.hazard_active:
            self.hazard_active = True
            self.hazard_start_time = current_time_ms
            self.fire_last_growth_time = current_time_ms
            self.fire_rows_completed = 0
            self.fire_row_length = 0
            return

        if self.fire_rows_completed >= self.MAX_FIRE_ROWS:
            return

        if current_time_ms - self.fire_last_growth_time >= 500:
            self.fire_last_growth_time = current_time_ms

            self.fire_row_length += 1

            if self.fire_row_length >= self.MAX_FIRE_ROW_LENGTH:
                self.fire_row_length = 0
                self.fire_rows_completed += 1

    def update_hazard_damage(self, surface_height: int) -> None:
        if not self.hazard_active:
            return

        tile_size = 32
        offset = 50
        damage = 5
        h = surface_height

        player_screen_rect = pygame.Rect(
            self.camera.world_to_screen_x(self.starship.hitbox.x),
            self.camera.world_to_screen_y(self.starship.hitbox.y),
            self.starship.hitbox.width,
            self.starship.hitbox.height
        )

        # 1️⃣ Damage completed rows
        for row in range(self.fire_rows_completed):
            y = h - offset - (row + 1) * tile_size
            for col in range(self.MAX_FIRE_ROW_LENGTH):
                x = col * tile_size
                rect = pygame.Rect(x, y, tile_size, tile_size)

                if rect.colliderect(player_screen_rect):
                    if not self.starship.invincible:
                        # ✅ APPLY TO SHIELDS FIRST (fallback to shipHealth if no shields)
                        if hasattr(self.starship, "shields") and self.starship.shields > 0:
                            self.starship.shields = max(0, self.starship.shields - damage)
                        elif hasattr(self.starship, "shield") and self.starship.shield > 0:
                            self.starship.shield = max(0, self.starship.shield - damage)
                        else:
                            self.starship.shipHealth -= damage

                        self.starship.on_hit()
                    return

        if self.fire_rows_completed < self.MAX_FIRE_ROWS:
            y = h - offset - (self.fire_rows_completed + 1) * tile_size
            for col in range(self.fire_row_length):
                x = col * tile_size
                rect = pygame.Rect(x, y, tile_size, tile_size)

                if rect.colliderect(player_screen_rect):
                    if not self.starship.invincible:
                        # ✅ APPLY TO SHIELDS FIRST (fallback to shipHealth if no shields)
                        if hasattr(self.starship, "shields") and self.starship.shields > 0:
                            self.starship.shields = max(0, self.starship.shields - damage)
                        elif hasattr(self.starship, "shield") and self.starship.shield > 0:
                            self.starship.shield = max(0, self.starship.shield - damage)
                        else:
                            self.starship.shipHealth -= damage

                        self.starship.on_hit()
                    return

    def update_rescue_pod_helper(self, state):
        for pod in list(self.rescue_pods):
            pod.update(state)
            if self.starship.hitbox.colliderect(pod.hitbox):
                self.rescue_pods.remove(pod)

    def draw_hazard_square(self, surface: pygame.Surface, camera) -> None:
        if not self.hazard_active:
            return

        tile_size = 32
        offset = 50
        h = surface.get_height()

        sprite_rect = pygame.Rect(65, 130, 32, 32)
        base_sprite = self.flame_image.subsurface(sprite_rect)
        sprite = pygame.transform.scale(base_sprite, (tile_size, tile_size))

        for row in range(self.fire_rows_completed):
            y = h - offset - (row + 1) * tile_size
            for col in range(self.MAX_FIRE_ROW_LENGTH):
                x = col * tile_size
                surface.blit(sprite, (x, y))

        if self.fire_rows_completed < self.MAX_FIRE_ROWS:
            y = h - offset - (self.fire_rows_completed + 1) * tile_size
            for col in range(self.fire_row_length):
                x = col * tile_size
                surface.blit(sprite, (x, y))

    def update_enemy_helper(self, state):
        for enemy in list(state.enemies):
            for pod in list(self.rescue_pods):
                if isinstance(enemy, RescuePod) and enemy == pod:
                    continue
                if enemy.hitbox.colliderect(pod.hitbox):
                    if pod in self.rescue_pods:
                        self.rescue_pods.remove(pod)
                        self.rescue_pod_destroyed += 1
                    break

        for enemy in list(state.enemies):
            result = enemy.update(state)

            if hasattr(enemy, "update_hitbox"):
                enemy.update_hitbox()

            if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                state.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            if result is not None:
                state.enemy_bullets.append(result)

            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)
                if not self.starship.invincible:
                    # ✅ APPLY TO SHIELDS FIRST (fallback to shipHealth if no shields)
                    if hasattr(self.starship, "shields") and self.starship.shields > 0:
                        self.starship.shields = max(0, self.starship.shields - enemy.touch_damage)
                    elif hasattr(self.starship, "shield") and self.starship.shield > 0:
                        self.starship.shield = max(0, self.starship.shield - enemy.touch_damage)
                    else:
                        self.starship.shipHealth -= enemy.touch_damage

                    self.starship.on_hit()
            else:
                enemy.color = GlobalConstants.RED

            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

    def draw_player_and_enemy(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)
            if hasattr(enemy, "draw_damage_flash"):
                enemy.draw_damage_flash(state.DISPLAY, self.camera)
        for pod in self.rescue_pods:
            pod.draw(state.DISPLAY, self.camera)

    def load_enemy_into_list(self,state):
        state.enemies.clear()
        self.rescue_pods.clear()

        for obj in self.tiled_map.objects:
            enemy = None

            if obj.name == "level_5_boss":
                enemy = BossLevelFive()

            elif obj.name == "rescue_pod":
                rescue_pod = RescuePod()
                rescue_pod.x = obj.x
                rescue_pod.y = obj.y
                rescue_pod.width = obj.width
                rescue_pod.height = obj.height
                rescue_pod.update_hitbox()
                rescue_pod.camera = self.camera
                rescue_pod.target_player = self.starship
                self.rescue_pods.append(rescue_pod)
                continue

            elif obj.name == "spinal_raptor":
                enemy = SpinalRaptor()
                enemy.rescue_pod_group = self.rescue_pods

            elif obj.name == "wasp_stinger":
                enemy = WaspStinger()

            elif obj.name == "ravager":
                enemy = Ravager()

            elif obj.name == "bile_spitter":
                enemy = BileSpitter()

            elif obj.name == "acid_launcher":
                enemy = AcidLauncher()

            elif obj.name == "spine_launcher":
                enemy = SpineLauncher()

            if enemy is None:
                continue

            enemy.x = obj.x
            enemy.y = obj.y
            enemy.width = obj.width
            enemy.height = obj.height
            enemy.update_hitbox()
            enemy.camera = self.camera
            enemy.target_player = self.starship
            state.enemies.append(enemy)

    def is_boss_on_screen(self, state) -> bool:
        cam_top = self.camera.y
        cam_bottom = cam_top + GlobalConstants.GAMEPLAY_HEIGHT

        for boss in state.enemies:
            if not isinstance(boss, BossLevelFive):
                continue
            boss_top = boss.y
            boss_bottom = boss.y + boss.height
            if boss_bottom >= cam_top and boss_top <= cam_bottom:
                return True
        return False


