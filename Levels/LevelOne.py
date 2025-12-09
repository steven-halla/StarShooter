import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.TriSpitter import TriSpitter
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelOne(VerticalBattleScreen):
    def __init__(self):
        super().__init__()

        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level1.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height

        # below is y POosition of map
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400

        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        # look at the bottom of the map
        self.camera_y = self.WORLD_HEIGHT - window_height

        # keep the Camera object in sync too
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        # self.move_screen_speed: float = .5


        # how many pixels the camera moves up per frame
        self.map_scroll_speed_per_frame: float = .4

        self.bileSpitterGroup: list[BileSpitter] = []
        self.kamikazeDroneGroup: list[KamikazeDrone] = []
        self.triSpitterGroup: list[TriSpitter] = []

        self.load_enemy_into_list()

    def start(self, state) -> None:
        # --- LOAD PLAYER SPAWN FROM TILED ---
        player_x = None
        player_y = None

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # <-- You placed this in Tiled
                player_x = obj.x
                player_y = obj.y
                break

        # SAFETY: If player object not found, fallback
        # if player_x is None or player_y is None:
        #     print("ERROR: No 'player' object found in Tiled map!")
        #     player_x = 300
        #     player_y = 355

        # APPLY PLAYER POSITION
        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐


    def update(self, state) -> None:
        # run all the normal gameplay logic from the parent
        super().update(state)
        self.enemy_helper()

        self.bullet_helper()


    def draw(self, state):
        # print("DRAWING INSTANCE:", id(self.starship))
        # --- 1. Call parent draw (this draws background + bullets) ---
        super().draw(state)

        zoom = self.camera.zoom

        # --- 2. Draw Tiled OBJECTS (like decorations, NOT the player) ---
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

    def load_enemy_into_list(self):
        print("LOAD BILE SPITTERS FUNCTION RAN!")

        for obj in self.tiled_map.objects:
            # ⭐ LOAD ENEMIES (existing code)
            if obj.name == "bile_spitter":
                enemy = BileSpitter()
                enemy.x = obj.x
                enemy.y = obj.y

                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()

                # ⭐ REQUIRED — THIS WAS MISSING
                enemy.camera = self.camera

                self.bileSpitterGroup.append(enemy)

            if obj.name == "kamikazi_drone":
                drone = KamikazeDrone()
                drone.x = obj.x
                drone.y = obj.y
                drone.width = obj.width
                drone.height = obj.height
                drone.update_hitbox()

                # ⭐ Add to the *correct* group
                self.kamikazeDroneGroup.append(drone)

                # ⭐ Set required references
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

                # ⭐ Add to the *correct* group
                self.triSpitterGroup.append(enemy_tri_spitter)

                # ⭐ Set required references
                enemy_tri_spitter.camera = self.camera
                enemy_tri_spitter.target_player = self.starship

                continue

    def enemy_helper(self):
        for drone in list(self.kamikazeDroneGroup):
            drone.update()

            if drone.enemyHealth <= 0:
                self.kamikazeDroneGroup.remove(drone)
                continue

        for enemy in self.bileSpitterGroup:
            enemy.update()
            # print("PLAYER HITBOX:", self.starship.hitbox)
            # print("ENEMY HITBOX:", enemy.hitbox)
            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)  # SKYBLUE
            else:

                enemy.color = GlobalConstants.RED
            enemy.update_hitbox()

            if enemy.enemyBullets:  # enemy fired bullets
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.update()
            # print("PLAYER HITBOX:", self.starship.hitbox)
            # print("ENEMY HITBOX:", enemy.hitbox)
            if self.starship.hitbox.colliderect(enemy_tri_spitter.hitbox):
                enemy_tri_spitter.color = (135, 206, 235)  # SKYBLUE
            else:

                enemy_tri_spitter.color = GlobalConstants.RED
            enemy_tri_spitter.update_hitbox()

            if enemy_tri_spitter.enemyBullets:  # enemy fired bullets
                self.enemy_bullets.extend(enemy_tri_spitter.enemyBullets)
                enemy_tri_spitter.enemyBullets.clear()

    def bullet_helper(self):

        # -------------------------------------------------------------
        # 🔥 ADDED: PLAYER BULLET COLLISIONS
        # -------------------------------------------------------------
        for bullet in list(self.player_bullets):

            # Convert bullet to SCREEN space
            b_rect = pygame.Rect(
                self.camera.world_to_screen_x(bullet.x),
                self.camera.world_to_screen_y(bullet.y),
                int(bullet.width * self.camera.zoom),
                int(bullet.height * self.camera.zoom)
            )

            # ---------------------------------------------
            # 🔥 PLAYER BULLET → KAMIKAZE DRONE COLLISION
            # ---------------------------------------------
            for drone in list(self.kamikazeDroneGroup):

                # convert drone to screen rect
                d_rect = pygame.Rect(
                    self.camera.world_to_screen_x(drone.x),
                    self.camera.world_to_screen_y(drone.y),
                    int(drone.width * self.camera.zoom),
                    int(drone.height * self.camera.zoom)
                )

                if b_rect.colliderect(d_rect):
                    drone.enemyHealth -= self.starship.bulletDamage
                    bullet.is_active = False

                    print("DRONE HIT! New HP =", drone.enemyHealth)

                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)

                    if drone.enemyHealth <= 0:
                        self.kamikazeDroneGroup.remove(drone)

                    break

            for enemy in list(self.bileSpitterGroup):

                # Convert enemy to SCREEN space
                e_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                # print("BULLET RECT:", b_rect)
                # print("ENEMY RECT:", e_rect)
                if b_rect.colliderect(e_rect):
                    enemy.enemyHealth -= self.starship.bulletDamage
                    bullet.is_active = False

                    print("HIT! New enemy HP =", enemy.enemyHealth)

                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)

                    if enemy.enemyHealth <= 0:
                        self.bileSpitterGroup.remove(enemy)

                    break

            for enemy in list(self.triSpitterGroup):

                # Convert enemy to SCREEN space
                e_rect = pygame.Rect(
                    self.camera.world_to_screen_x(enemy.x),
                    self.camera.world_to_screen_y(enemy.y),
                    int(enemy.width * self.camera.zoom),
                    int(enemy.height * self.camera.zoom)
                )

                # print("BULLET RECT:", b_rect)
                # print("ENEMY RECT:", e_rect)
                if b_rect.colliderect(e_rect):
                    enemy.enemyHealth -= self.starship.bulletDamage
                    bullet.is_active = False

                    print("HIT! New enemy HP =", enemy.enemyHealth)

                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)

                    if enemy.enemyHealth <= 0:
                        self.triSpitterGroup.remove(enemy)

                    break
        # -------------------------------------------------------------
        # 🔥 ADDED: ENEMY BULLET → PLAYER COLLISION
        # -------------------------------------------------------------
        for bullet in list(self.enemy_bullets):
            if bullet.collide_with_rect(self.starship.hitbox):
                self.starship.shipHealth -= bullet.damage
                bullet.is_active = False

                if self.starship.shipHealth <= 0:
                    self.playerDead = True

                self.enemy_bullets.remove(bullet)
        # DEBUG: Check if player & enemy share same Y tile
        tile_h = self.tile_size

        player_row = int(self.starship.y // tile_h)
        if self.bileSpitterGroup:  # if list is not empty
            first_enemy = self.bileSpitterGroup[0]
            enemy_row = int(first_enemy.y // tile_h)


