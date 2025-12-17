import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.TriSpitter import TriSpitter
from Entity.StarShip import StarShip
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelOne(VerticalBattleScreen):
    def __init__(self):
        super().__init__()
        # self.starship: StarShip = StarShip()

        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level1.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400 # y position of map
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        self.camera_y = self.WORLD_HEIGHT - window_height # look at bottom of map
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = .4 # move speed of camera
        self.bileSpitterGroup: list[BileSpitter] = []
        self.kamikazeDroneGroup: list[KamikazeDrone] = []
        self.triSpitterGroup: list[TriSpitter] = []
        # self.load_enemy_into_list()

    def start(self, state) -> None:
        player_x = None
        player_y = None

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list()


    def update(self, state) -> None:
        super().update(state)
        # Missile firing (override parent behavior)
        if self.controller.fire_missiles:
            missile = self.starship.fire_missile()
            if missile is not None:

                # Lock onto nearest enemy
                missile.target_enemy = self.get_nearest_enemy(missile)

                # Compute initial direction toward target
                if missile.target_enemy is not None:
                    dx = missile.target_enemy.x - missile.x
                    dy = missile.target_enemy.y - missile.y
                    dist = max(1, (dx * dx + dy * dy) ** 0.5)
                    missile.direction_x = dx / dist
                    missile.direction_y = dy / dist
                else:
                    # No enemy → missile goes straight upward
                    missile.direction_x = 0
                    missile.direction_y = -1

                # Add to missile list
                self.player_missiles.append(missile)

                if missile.target_enemy is not None:
                    print(f"Missile locked onto: {type(missile.target_enemy).__name__} "
                          f"at ({missile.target_enemy.x}, {missile.target_enemy.y})")
                else:
                    print("Missile locked onto: NONE (no enemies found)")
        self.enemy_helper()

        self.bullet_helper()

        self.extract_object_names()


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

        for enemy in self.bileSpitterGroup:
            enemy.draw(state.DISPLAY, self.camera)

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.draw(state.DISPLAY, self.camera)

        for drone in self.kamikazeDroneGroup:
            drone.draw(state.DISPLAY, self.camera)

        for enemy_tri_spitter in self.triSpitterGroup:
            hb = pygame.Rect(
                self.camera.world_to_screen_x(enemy_tri_spitter.hitbox.x),
                self.camera.world_to_screen_y(enemy_tri_spitter.hitbox.y),
                int(enemy_tri_spitter.hitbox.width * zoom),
                int(enemy_tri_spitter.hitbox.height * zoom)
            )
            pygame.draw.rect(state.DISPLAY, (255, 255, 0), hb, 2)

        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        enemies = (
                list(self.bileSpitterGroup) +
                list(self.kamikazeDroneGroup) +
                list(self.triSpitterGroup)
        )

        if not enemies:
            return None

        # Visible camera bounds (world coordinates)
        visible_top = self.camera.y
        visible_bottom = self.camera.y + (self.window_height / self.camera.zoom)

        nearest_enemy = None
        nearest_dist = float("inf")
        mx, my = missile.x, missile.y

        for enemy in enemies:

            # ⛔ Skip enemies outside the screen
            if enemy.y + enemy.height < visible_top:
                continue  # enemy is above screen
            if enemy.y > visible_bottom:
                continue  # enemy is below screen

            # distance calculation
            dx = enemy.x - mx
            dy = enemy.y - my
            dist_sq = dx * dx + dy * dy

            if dist_sq < nearest_dist:
                nearest_dist = dist_sq
                nearest_enemy = enemy

        return nearest_enemy

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

    def load_enemy_into_list(self):
        for obj in self.tiled_map.objects:
            # ⭐ LOAD ENEMIES (existing code)
            if obj.name == "bile_spitter":
                enemy = BileSpitter()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.bileSpitterGroup.append(enemy)

            if obj.name == "kamikazi_drone":
                drone = KamikazeDrone()
                drone.x = obj.x
                drone.y = obj.y
                drone.width = obj.width
                drone.height = obj.height
                drone.update_hitbox()
                self.kamikazeDroneGroup.append(drone)
                drone.camera = self.camera
                drone.target_player = self.starship
                continue

            if obj.name == "tri_spitter":
                enemy_tri_spitter = TriSpitter()
                enemy_tri_spitter.x = obj.x
                enemy_tri_spitter.y = obj.y
                enemy_tri_spitter.width = obj.width
                enemy_tri_spitter.height = obj.height
                enemy_tri_spitter.update_hitbox()
                self.triSpitterGroup.append(enemy_tri_spitter)
                enemy_tri_spitter.camera = self.camera
                enemy_tri_spitter.target_player = self.starship
                continue

    def enemy_helper(self):
        # -------------------------
        # METAL SHIELD → ENEMY BULLETS
        # -------------------------
        for metal in list(self.metal_shield_bullets):

            if not metal.is_active:
                self.metal_shield_bullets.remove(metal)
                continue

            # Build shield rect in WORLD space
            shield_rect = pygame.Rect(
                metal.x,
                metal.y,
                metal.width,
                metal.height
            )

            for bullet in list(self.enemy_bullets):

                # Enemy bullets already have a hitbox / rect logic
                if bullet.collide_with_rect(shield_rect):

                    # Shield absorbs the hit
                    absorbed = metal.absorb_hit()

                    # Remove enemy bullet
                    if bullet in self.enemy_bullets:
                        self.enemy_bullets.remove(bullet)

                    # Remove shield if it absorbed
                    if absorbed and metal in self.metal_shield_bullets:
                        self.metal_shield_bullets.remove(metal)

                    break  # one hit only

        for drone in list(self.kamikazeDroneGroup):
            drone.update()

            if drone.enemyHealth <= 0:
                self.kamikazeDroneGroup.remove(drone)
                continue

        for enemy in self.bileSpitterGroup:
            enemy.update()
            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)  # SKYBLUE
            else:
                enemy.color = GlobalConstants.RED
            enemy.update_hitbox()

            if enemy.enemyBullets:
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.update()
            if self.starship.hitbox.colliderect(enemy_tri_spitter.hitbox):
                enemy_tri_spitter.color = (135, 206, 235)  # SKYBLUE
            else:
                enemy_tri_spitter.color = GlobalConstants.RED
            enemy_tri_spitter.update_hitbox()

            if enemy_tri_spitter.enemyBullets:
                self.enemy_bullets.extend(enemy_tri_spitter.enemyBullets)
                enemy_tri_spitter.enemyBullets.clear()

    def bullet_helper(self):
        all_enemies = (
                list(self.kamikazeDroneGroup) +
                list(self.bileSpitterGroup) +
                list(self.triSpitterGroup)
        )
        # -------------------------
        # PLASMA BLASTER → ENEMY COLLISION
        # -------------------------
        for plasma in list(self.plasma_blaster_bullets):

            plasma_rect = pygame.Rect(
                self.camera.world_to_screen_x(plasma.x),
                self.camera.world_to_screen_y(plasma.y),
                int(plasma.width * self.camera.zoom),
                int(plasma.height * self.camera.zoom)
            )

            for enemy in all_enemies:

                enemy_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                if plasma_rect.colliderect(enemy_rect):
                    print("⚡ PLASMA BLASTER HIT", type(enemy).__name__)
                    enemy.enemyHealth -= plasma.damage

                    # if plasma in self.plasma_blaster_bullets:
                    #     self.plasma_blaster_bullets.remove(plasma)

                    if enemy.enemyHealth <= 0:
                        if enemy in self.kamikazeDroneGroup:
                            self.kamikazeDroneGroup.remove(enemy)
                        elif enemy in self.bileSpitterGroup:
                            self.bileSpitterGroup.remove(enemy)
                        elif enemy in self.triSpitterGroup:
                            self.triSpitterGroup.remove(enemy)

                    break  # plasma is gone, stop checking
        # -------------------------
        # WIND SLICER → ENEMY COLLISION
        # -------------------------
        for slicer in list(self.wind_slicer_bullets):

            slicer_rect = pygame.Rect(
                self.camera.world_to_screen_x(slicer.x),
                self.camera.world_to_screen_y(slicer.y),
                int(slicer.width * self.camera.zoom),
                int(slicer.height * self.camera.zoom)
            )

            for enemy in all_enemies:

                enemy_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                if slicer_rect.colliderect(enemy_rect):
                    print("🌪️ WIND SLICER HIT", type(enemy).__name__)

                    enemy.enemyHealth -= slicer.damage

                    # 🔥 WIND SLICER IS CONSUMED ON ENEMY HIT
                    if slicer in self.wind_slicer_bullets:
                        self.wind_slicer_bullets.remove(slicer)

                    if enemy.enemyHealth <= 0:
                        if enemy in self.kamikazeDroneGroup:
                            self.kamikazeDroneGroup.remove(enemy)
                        elif enemy in self.bileSpitterGroup:
                            self.bileSpitterGroup.remove(enemy)
                        elif enemy in self.triSpitterGroup:
                            self.triSpitterGroup.remove(enemy)

                    break  # slicer is gone, stop checking
        # -------------------------
        # WIND SLICER → ENEMY BULLET COLLISION
        # -------------------------
        for slicer in list(self.wind_slicer_bullets):

            slicer_rect = pygame.Rect(
                self.camera.world_to_screen_x(slicer.x),
                self.camera.world_to_screen_y(slicer.y),
                int(slicer.width * self.camera.zoom),
                int(slicer.height * self.camera.zoom)
            )

            for enemy_bullet in list(self.enemy_bullets):

                enemy_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy_bullet.x),
                    self.camera.world_to_screen_y(enemy_bullet.y),
                    int(enemy_bullet.width * self.camera.zoom),
                    int(enemy_bullet.height * self.camera.zoom)
                )

                if slicer_rect.colliderect(enemy_rect):
                    print("🌪️ WIND SLICER CUT BULLET")

                    self.enemy_bullets.remove(enemy_bullet)
                    self.wind_slicer_bullets.remove(slicer)

                    break

        # -------------------------
        # ENERGY BALL → ENEMY COLLISION
        # -------------------------

        for ball in list(self.energy_balls):

            ball_rect = pygame.Rect(
                self.camera.world_to_screen_x(ball.x),
                self.camera.world_to_screen_y(ball.y),
                int(ball.width * self.camera.zoom),
                int(ball.height * self.camera.zoom)
            )

            for enemy in all_enemies:

                enemy_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                if ball_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= ball.damage
                    ball.is_active = False

                    if ball in self.energy_balls:
                        self.energy_balls.remove(ball)

                    if enemy.enemyHealth <= 0:
                        if enemy in self.kamikazeDroneGroup:
                            self.kamikazeDroneGroup.remove(enemy)
                        elif enemy in self.bileSpitterGroup:
                            self.bileSpitterGroup.remove(enemy)
                        elif enemy in self.triSpitterGroup:
                            self.triSpitterGroup.remove(enemy)

                    break  # ball is gone, stop checking

        # -------------------------
        # HYPER LASER → ENEMY COLLISION
        # -------------------------
        for laser in list(self.hyper_laser_bullets):

            laser_rect = pygame.Rect(
                self.camera.world_to_screen_x(laser.x),
                self.camera.world_to_screen_y(laser.y),
                int(laser.width * self.camera.zoom),
                int(laser.height * self.camera.zoom)
            )

            for enemy in all_enemies:

                enemy_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                if laser_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= self.starship.hyper_laser_damage
                    laser.is_active = False

                    if laser in self.hyper_laser_bullets:
                        self.hyper_laser_bullets.remove(laser)

                    if enemy.enemyHealth <= 0:
                        if enemy in self.kamikazeDroneGroup:
                            self.kamikazeDroneGroup.remove(enemy)
                        elif enemy in self.bileSpitterGroup:
                            self.bileSpitterGroup.remove(enemy)
                        elif enemy in self.triSpitterGroup:
                            self.triSpitterGroup.remove(enemy)

                    break  # laser is gone, stop checking

        # -------------------------
        # METAL SHIELD → ENEMY COLLISION
        # -------------------------

        for metal in list(self.metal_shield_bullets):

            metal_rect = pygame.Rect(
                self.camera.world_to_screen_x(metal.x),
                self.camera.world_to_screen_y(metal.y),
                int(metal.width * self.camera.zoom),
                int(metal.height * self.camera.zoom)
            )

            for enemy in all_enemies:

                enemy_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                if metal_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= self.starship.missileDamage
                    metal.is_active = False

                    if metal in self.metal_shield_bullets:
                        self.metal_shield_bullets.remove(metal)

                    if enemy.enemyHealth <= 0:
                        if enemy in self.kamikazeDroneGroup:
                            self.kamikazeDroneGroup.remove(enemy)
                        elif enemy in self.bileSpitterGroup:
                            self.bileSpitterGroup.remove(enemy)
                        elif enemy in self.triSpitterGroup:
                            self.triSpitterGroup.remove(enemy)

                    break  # shield is gone, stop checking
        # -------------------------
        # MISSILE → ENEMY COLLISION
        # -------------------------

        for missile in list(self.player_missiles):

            missile_rect = pygame.Rect(
                self.camera.world_to_screen_x(missile.x),
                self.camera.world_to_screen_y(missile.y),
                int(missile.width * self.camera.zoom),
                int(missile.height * self.camera.zoom)
            )

            for enemy in all_enemies:

                enemy_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                if missile_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= self.starship.missileDamage
                    missile.is_active = False

                    if missile in self.player_missiles:
                        self.player_missiles.remove(missile)

                    if enemy.enemyHealth <= 0:
                        if enemy in self.kamikazeDroneGroup:
                            self.kamikazeDroneGroup.remove(enemy)
                        elif enemy in self.bileSpitterGroup:
                            self.bileSpitterGroup.remove(enemy)
                        elif enemy in self.triSpitterGroup:
                            self.triSpitterGroup.remove(enemy)

                    break  # missile is gone, stop checking

        # -------------------------
        # NAPALM SPREAD → ENEMY COLLISION / AOE
        # -------------------------
        for napalm in list(self.napalm_spread_bullets):

            napalm_rect = pygame.Rect(
                napalm.x,
                napalm.y,
                napalm.width,
                napalm.height
            )

            # ----------------------------------
            # DIRECT HIT → FORCE EXPLOSION
            # ----------------------------------
            if not napalm.has_exploded:

                all_enemies = (
                        list(self.kamikazeDroneGroup) +
                        list(self.bileSpitterGroup) +
                        list(self.triSpitterGroup)
                )

                for enemy in all_enemies:
                    if napalm_rect.colliderect(enemy.hitbox):
                        napalm.has_exploded = True
                        napalm.explosion_timer.reset()
                        enemy.enemyHealth -= napalm.damage

                        if enemy.enemyHealth <= 0:
                            if enemy in self.kamikazeDroneGroup:
                                self.kamikazeDroneGroup.remove(enemy)
                            elif enemy in self.bileSpitterGroup:
                                self.bileSpitterGroup.remove(enemy)
                            elif enemy in self.triSpitterGroup:
                                self.triSpitterGroup.remove(enemy)

                        break  # only ONE direct-hit explosion

            # ----------------------------------
            # EXPLOSION AOE DAMAGE (ONCE)
            # ----------------------------------
            if napalm.has_exploded and not napalm.aoe_applied:

                # 💥 Explosion center (WORLD space)
                cx = napalm.x + napalm.width // 2
                cy = napalm.y + napalm.height // 2

                aoe_rect = pygame.Rect(
                    cx - napalm.area_of_effect_x // 2,
                    cy - napalm.area_of_effect_y // 2,
                    napalm.area_of_effect_x,
                    napalm.area_of_effect_y
                )

                all_enemies = (
                        list(self.kamikazeDroneGroup) +
                        list(self.bileSpitterGroup) +
                        list(self.triSpitterGroup)
                )

                for enemy in all_enemies:

                    enemy_hitbox = pygame.Rect(
                        enemy.x,
                        enemy.y,
                        enemy.width,
                        enemy.height
                    )

                    if aoe_rect.colliderect(enemy_hitbox):
                        print("🔥 NAPALM AOE HIT:", type(enemy).__name__)
                        enemy.enemyHealth -= napalm.damage

                        if enemy.enemyHealth <= 0:
                            if enemy in self.kamikazeDroneGroup:
                                self.kamikazeDroneGroup.remove(enemy)
                            elif enemy in self.bileSpitterGroup:
                                self.bileSpitterGroup.remove(enemy)
                            elif enemy in self.triSpitterGroup:
                                self.triSpitterGroup.remove(enemy)

                # 🔒 AOE MUST ONLY APPLY ONCE
                napalm.aoe_applied = True
            # ----------------------------------
            # EXPLOSION AOE DAMAGE (LINGERING)
            # ----------------------------------
            if napalm.has_exploded and not napalm.explosion_timer.is_ready():

                cx = napalm.x + napalm.width // 2
                cy = napalm.y + napalm.height // 2

                aoe_rect = pygame.Rect(
                    cx - napalm.area_of_effect_x // 2,
                    cy - napalm.area_of_effect_y // 2,
                    napalm.area_of_effect_x,
                    napalm.area_of_effect_y
                )

                all_enemies = (
                        list(self.kamikazeDroneGroup) +
                        list(self.bileSpitterGroup) +
                        list(self.triSpitterGroup)
                )

                for enemy in all_enemies:

                    if aoe_rect.colliderect(enemy.hitbox):
                        print(
                            "🔥 NAPALM BURNING:",
                            type(enemy).__name__,
                            "AOE:", aoe_rect,
                            "ENEMY:", enemy.hitbox
                        )

                        enemy.enemyHealth -= napalm.damage

                        if enemy.enemyHealth <= 0:
                            print("💀 NAPALM KILL:", type(enemy).__name__)

                            if enemy in self.kamikazeDroneGroup:
                                self.kamikazeDroneGroup.remove(enemy)
                            elif enemy in self.bileSpitterGroup:
                                self.bileSpitterGroup.remove(enemy)
                            elif enemy in self.triSpitterGroup:
                                self.triSpitterGroup.remove(enemy)

        # -------------------------
        # BUSTER CANNON → ENEMY COLLISION
        # -------------------------

        for bc in list(self.buster_cannon_bullets):

            bc_rect = pygame.Rect(
                self.camera.world_to_screen_x(bc.x),
                self.camera.world_to_screen_y(bc.y),
                int(bc.width * self.camera.zoom),
                int(bc.height * self.camera.zoom)
            )

            for enemy in all_enemies:

                enemy_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                if bc_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= bc.damage
                    bc.is_active = False

                    if bc in self.buster_cannon_bullets:
                        self.buster_cannon_bullets.remove(bc)

                    if enemy.enemyHealth <= 0:
                        if enemy in self.kamikazeDroneGroup:
                            self.kamikazeDroneGroup.remove(enemy)
                        elif enemy in self.bileSpitterGroup:
                            self.bileSpitterGroup.remove(enemy)
                        elif enemy in self.triSpitterGroup:
                            self.triSpitterGroup.remove(enemy)

                    break

        # -------------------------
        # PLAYER BULLETS → ENEMY COLLISION
        # -------------------------

        for bullet in list(self.player_bullets):

            b_rect = pygame.Rect(
                self.camera.world_to_screen_x(bullet.x),
                self.camera.world_to_screen_y(bullet.y),
                int(bullet.width * self.camera.zoom),
                int(bullet.height * self.camera.zoom)
            )

            for enemy in all_enemies:

                enemy_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                if b_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= self.starship.bulletDamage
                    bullet.is_active = False

                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)

                    if enemy.enemyHealth <= 0:
                        if enemy in self.kamikazeDroneGroup:
                            self.kamikazeDroneGroup.remove(enemy)
                        elif enemy in self.bileSpitterGroup:
                            self.bileSpitterGroup.remove(enemy)
                        elif enemy in self.triSpitterGroup:
                            self.triSpitterGroup.remove(enemy)

                    break
        # -------------------------
        # WAVE CRASH → ENEMY COLLISION
        # -------------------------
        for wave in list(self.wave_crash_bullets):

            w_rect = pygame.Rect(
                self.camera.world_to_screen_x(wave.x),
                self.camera.world_to_screen_y(wave.y),
                int(wave.width * self.camera.zoom),
                int(wave.height * self.camera.zoom)
            )

            for enemy in all_enemies:

                enemy_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                if w_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= wave.damage
                    wave.is_active = False

                    if wave in self.wave_crash_bullets:
                        self.wave_crash_bullets.remove(wave)

                    if enemy.enemyHealth <= 0:
                        if enemy in self.kamikazeDroneGroup:
                            self.kamikazeDroneGroup.remove(enemy)
                        elif enemy in self.bileSpitterGroup:
                            self.bileSpitterGroup.remove(enemy)
                        elif enemy in self.triSpitterGroup:
                            self.triSpitterGroup.remove(enemy)

                    break
