import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Bosses.BossLevelSix import BossLevelSix
from Entity.Monsters.Coins import Coins
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.SpikeyBall import SpikeyBall
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.SpinalRaptor import SpinalRaptor
from Entity.Monsters.TransportWorm import TransportWorm
from SaveStates.SaveState import SaveState
from ScreenClasses.HomeBase import HomeBase
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
        # self.camera_y =  90 # look at bottom of map
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
        self.all_potential_enemies = []
        self.coins_collected: int = 0
        self.boss_death_timer = None


    def start(self, state) -> None:
        player_x = None
        player_y = None
        state.starship.shipHealth = state.starship.shipHealthMax
        state.starship.shield_system.reset()
        state.starship.player_ki = state.starship.player_max_ki
        state.starship.missile.current_missiles = state.starship.missile.max_missiles
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
        self.save_state.set_location_level(6, screen_name="Level 6")
        self.save_state.capture_player(self.starship)
        self.save_state.save_to_file("player_save.json")

    def update(self, state) -> None:
        # print(sum(1 for e in state.enemies if getattr(e, "name", "") == "Coins"))
        self.update_handle_level_complete(state)

        if self.boss_death_timer is not None:
            # print(f"[DEBUG LevelSix] boss_death_timer time left: {self.boss_death_timer.get_time_left()}")
            if self.boss_death_timer.is_ready():
                state.starship.money += 1000 * self.coins_collected
                state.currentScreen = HomeBase(self.textbox)
                state.currentScreen.start(state)
                return
        #CLEAN OUT EXPECT4D ENEMIES LIST AFTER WE KILL BOSS

        super().update(state)
        self.update_collision_tiles(state, damage=5)

        # Move enemies from all_potential_enemies to state.enemies when they are in vicinity
        cam_top = self.camera.y
        cam_bottom = cam_top + GlobalConstants.GAMEPLAY_HEIGHT
        buffer = 150  # Load enemies slightly before they appear on screen

        for enemy in list(self.all_potential_enemies):
            # Check if the enemy is within player vicinity (near screen area)
            if (enemy.y + enemy.height >= cam_top - buffer) and (enemy.y <= cam_bottom + buffer):
                state.enemies.append(enemy)
                self.all_potential_enemies.remove(enemy)

        self.update_check_player_touching_collision_bottom()
        self.update_assign_single_barrage_owner(state)
        self.update_player_touches_coin(state)
        self.update_enemy_helper(state)
        self.update_worm_helper(state)

    def draw(self, state):
        super().draw(state)
        self.draw_player_enemies(state)
        self.draw_coin_counter(state)
        pygame.display.flip()

    def update_handle_level_complete(self, state):
        if not self.level_complete:
            # Check all_potential_enemies AND state.enemies for the boss
            # This handles the boss whether it has spawned yet or not
            boss = next((e for e in self.all_potential_enemies + state.enemies if isinstance(e, BossLevelSix)), None)

            if boss:
                print(f"[DEBUG LevelSix] Found boss. enemyHealth: {boss.enemyHealth}, boss_dead: {boss.boss_dead}")
                if boss.boss_dead:
                    print(f"[DEBUG LevelSix] Boss dead! Starting timer. boss_death_timer: {self.boss_death_timer}")
                    if self.boss_death_timer is None:
                        print("[DEBUG LevelSix] Initializing boss_death_timer.")
                        self.boss_death_timer = Timer(2.0)
                        self.boss_death_timer.reset()
                        self.level_complete = True

                    # Ensure boss is removed from enemies list so it doesn't keep updating/drawing
                    if boss in state.enemies:
                        print("[DEBUG LevelSix] Removing boss from state.enemies")
                        state.enemies.remove(boss)
                elif boss.enemyHealth <= 0:
                    print(f"[DEBUG LevelSix] Boss health is {boss.enemyHealth} but boss_dead is False. Forcing boss_dead = True")
                    boss.boss_dead = True

    def draw_coin_counter(self, state):
        font = pygame.font.Font(None, 28)
        coin_text = font.render(
            f"Coins: {self.coins_collected}",
            True,
            GlobalConstants.WHITE
        )
        state.DISPLAY.blit(coin_text, (10, 10))

    def update_enemy_helper(self, state):
        cam_top = self.camera.y
        cam_bottom = cam_top + GlobalConstants.GAMEPLAY_HEIGHT
        update_buffer = 150 # Match load buffer

        for enemy in list(state.enemies):
            # Only update if in vicinity of the camera
            if not ((enemy.y + enemy.height >= cam_top - update_buffer) and (enemy.y <= cam_bottom + update_buffer)):
                continue

            if isinstance(enemy, Coins):
                # Coins are handled in update_player_touches_coin
                continue

            if isinstance(enemy, BossLevelSix):
                enemy.update(state, self.starship)
                enemy.apply_barrage_damage(self.starship)

                if self.starship.hitbox.colliderect(enemy.hitbox):
                    if not self.starship.invincible:
                        self.starship.shield_system.take_damage(enemy.touch_damage)
                        self.starship.on_hit()

                if enemy.enemyBullets:
                    state.enemy_bullets.extend(enemy.enemyBullets)
                    enemy.enemyBullets.clear()

            elif isinstance(enemy, SpikeyBall):
                enemy.update(state)

                if self.starship.hitbox.colliderect(enemy.hitbox):
                    enemy.color = (135, 206, 235)
                    if not self.starship.invincible:
                        self.starship.shipHealth -= 45
                        self.starship.on_hit()
                else:
                    enemy.color = GlobalConstants.RED
            else:
                # General update for other enemies (SpinalRaptor, BileSpitter, TransportWorm, FireLauncher)
                result = enemy.update(state)

                if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                    state.enemy_bullets.extend(enemy.enemyBullets)
                    enemy.enemyBullets.clear()

                if result is not None:
                    # Some older enemies might return a single bullet
                    from Weapons.Bullet import Bullet
                    if isinstance(result, Bullet):
                        state.enemy_bullets.append(result)

                if self.starship.hitbox.colliderect(enemy.hitbox):
                    if not self.starship.invincible:
                        touch_damage = getattr(enemy, "touch_damage", 10)
                        self.starship.shield_system.take_damage(touch_damage)
                        self.starship.on_hit()

            if hasattr(enemy, "enemyHealth") and enemy.enemyHealth <= 0:
                self.remove_enemy_if_dead(enemy, state)

    def update_worm_helper(self, state):
        now = pygame.time.get_ticks()
        player = self.starship
        active_worms = [e for e in state.enemies if isinstance(e, TransportWorm) and e.is_active]

        for worm in active_worms:
            # check distance
            dist_y = abs(player.y - worm.y)

            # DEBUG PRINTS using camera
            p_sx = self.camera.world_to_screen_x(player.x)
            p_sy = self.camera.world_to_screen_y(player.y)
            w_sx = self.camera.world_to_screen_x(worm.x)
            w_sy = self.camera.world_to_screen_y(worm.y)
            # print(f"[DEBUG] Player Screen: ({p_sx:.1f}, {p_sy:.1f}), Worm Screen: ({w_sx:.1f}, {w_sy:.1f}), DistY: {dist_y:.1f}")

            if dist_y < 300:
                if now - worm.last_summon_time >= worm.summon_interval_ms:
                    worm.summon_enemy(
                        enemy_classes=[
                            BileSpitter,
                            SpikeyBall
                        ],
                        enemy_groups={
                            BileSpitter: state.enemies,
                            SpikeyBall: state.enemies,
                        },
                        spawn_y_offset=20
                    )
                    worm.last_summon_time = now

    def update_player_touches_coin(self, state):
        for enemy in list(state.enemies):

            if not isinstance(enemy, Coins):
                continue

            if enemy.hitbox.colliderect(self.starship.hitbox):
                # print(f"[LAST COIN] x={enemy.x:.2f}, y={enemy.y:.2f}")
                self.coins_collected += 1
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
        cam_top = self.camera.y
        cam_bottom = cam_top + GlobalConstants.GAMEPLAY_HEIGHT
        buffer = 150

        bosses = [e for e in state.enemies if isinstance(e, BossLevelSix)]
        if not bosses:
            return

        for boss in bosses:
            boss.may_fire_barrage = False

        on_screen_bosses = [
            b for b in bosses
            if (b.y + b.height >= cam_top - buffer) and (b.y <= cam_bottom + buffer)
        ]

        if on_screen_bosses:
            on_screen_bosses[0].may_fire_barrage = True
        else:
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
        self.all_potential_enemies.clear()
        for obj in self.tiled_map.objects:
            if obj.name == "level_6_boss":
                enemy = BossLevelSix()

            elif obj.name == "spikey_ball":
                enemy = SpikeyBall()
            elif obj.name == "transport_worm":
                enemy = TransportWorm()
                enemy.is_active = True
            elif obj.name == "spinal_raptor":
                enemy = SpinalRaptor()
            elif obj.name == "bile_spitter":
                enemy = BileSpitter()
            elif obj.name == "fire_launcher":
                enemy = FireLauncher()

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
            self.all_potential_enemies.append(enemy)

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
