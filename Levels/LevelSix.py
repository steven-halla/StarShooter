import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelSix import BossLevelSix
from Entity.Monsters.Coins import Coins
from Entity.Monsters.SpikeyBall import SpikeyBall
from SaveStates.SaveState import SaveState
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen

class LevelSix(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)

        self.level_start:bool = True
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level6.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400 # y position of map
        window_height: int = GlobalConstants.GAMEPLAY_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - window_height # look at bottom of map
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.coins_missed = []
        self.flame_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.game_over: bool = False
        self.level_complete = False
        self.save_state = SaveState()
        self.may_fire_barrage: bool = True
        self.crush_start_time = None
        self.CRUSH_TIME_MS = 500

    def start(self, state) -> None:
        player_x = None
        player_y = None
        state.starship.current_level = 6

        for obj in self.tiled_map.objects:
            if obj.name == "player":
                player_x = obj.x
                player_y = obj.y
                break

        self.starship = state.starship

        if player_x is None or player_y is None:
            pass
        else:
            self.starship.x = player_x
            self.starship.y = player_y

        self.load_enemy_into_list(state)
        self.save_state.capture_player(self.starship, self.__class__.__name__)
        self.save_state.save_to_file("player_save.json")


    def update(self, state) -> None:
        super().update(state)
        self.update_check_player_touching_collision_bottom()
        self.update_assign_single_barrage_owner(state)
        self.update_player_touches_coin(state)
        self.update_enemy_helper(state)
        self.update_collision_tiles(state, damage=5)

    def draw(self, state):
        state.DISPLAY.fill((0, 0, 0))
        super().draw(state)
        self.draw_player_enemies(state)
        self.draw_ui_panel(state.DISPLAY)
        pygame.display.flip()

    def update_enemy_helper(self, state):
        for enemy in list(state.enemies):

            if not isinstance(enemy, BossLevelSix):
                continue

            enemy.update(self.starship)
            enemy.apply_barrage_damage(self.starship)

            if enemy.enemyBullets:
                state.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

        for enemy in list(state.enemies):
            if not isinstance(enemy, SpikeyBall):
                continue

            enemy.update(state)

            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)
                continue

            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)
                if not self.starship.invincible:
                    self.starship.shipHealth -= 5
                    self.starship.on_hit()
            else:
                enemy.color = GlobalConstants.RED

    def update_player_touches_coin(self, state):
        for enemy in list(state.enemies):

            if not isinstance(enemy, Coins):
                continue

            if enemy.hitbox.colliderect(self.starship.hitbox):
                print(f"[LAST COIN] x={enemy.x:.2f}, y={enemy.y:.2f}")
                enemy.is_active = False
                state.enemies.remove(enemy)
                continue

            screen_y = self.camera.world_to_screen_y(enemy.y)

            if screen_y > (GlobalConstants.GAMEPLAY_HEIGHT - 1):
                if enemy not in self.coins_missed:
                    self.coins_missed.append(enemy)

                enemy.is_active = False
                state.enemies.remove(enemy)

    def update_assign_single_barrage_owner(self, state) -> None:
        bosses = [e for e in state.enemies if isinstance(e, BossLevelSix)]

        if not bosses:
            return

        for boss in bosses:
            boss.may_fire_barrage = False

        bosses[0].may_fire_barrage = True

    def update_check_player_touching_collision_bottom(self) -> None:
        player = self.starship

        probe_below = pygame.Rect(
            player.hitbox.x,
            player.hitbox.bottom,
            player.hitbox.width,
            1
        )

    def draw_player_enemies(self, state):
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)

            if hasattr(enemy, "draw_damage_flash"):
                enemy.draw_damage_flash(state.DISPLAY, self.camera)

            if isinstance(enemy, BossLevelSix):
                enemy.draw_barrage(state.DISPLAY, self.camera)

    def draw_level_collision(self, surface: pygame.Surface) -> None:
        self.draw_collision_tiles(surface)

    def load_enemy_into_list(self, state):
        state.enemies.clear()
        for obj in self.tiled_map.objects:
            if obj.name == "level_6_boss":
                enemy = BossLevelSix()

            elif obj.name == "spikey_ball":
                enemy = SpikeyBall()

            elif obj.name == "coins":
                enemy = Coins()
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

    def is_boss_on_screen(self, state) -> bool:
        cam_top = self.camera.y
        cam_bottom = cam_top + GlobalConstants.GAMEPLAY_HEIGHT

        for enemy in state.enemies:
            if not isinstance(enemy, BossLevelSix):
                continue

            boss_top = enemy.y
            boss_bottom = enemy.y + enemy.height

            if boss_bottom >= cam_top and boss_top <= cam_bottom:
                return True

        return False
