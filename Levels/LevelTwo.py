import pygame
import pytmx
from pygame import Surface

from Constants.GlobalConstants import GlobalConstants
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.TriSpitter import TriSpitter
from ScreenClasses.Camera import Camera
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelTwo(VerticalBattleScreen):
    def __init__(self):
        super().__init__()
        # print("LEVEL ONE INIT EXECUTED")

        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level2.tmx")
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
        self.map_scroll_speed_per_frame: float = .8

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

        # DEBUG PRINT
        tile_size = self.tiled_map.tileheight
        map_width_tiles = self.tiled_map.width
        map_height_tiles = self.tiled_map.height

        col = int(player_x // tile_size)
        row = int(player_y // tile_size)

        print(
            f"Starship start at: col={col}, row={row} | "
            f"x={self.starship.x}, y={self.starship.y}, map={map_width_tiles}x{map_height_tiles} tiles"
        )


    def update(self, state) -> None:
        # run all the normal gameplay logic from the parent
        super().update(state)

        # print(self.starship.shipHealth)

        # super().update(state)

        # now handle map scroll ONLY in LevelOne
        # _, window_height = GlobalConstants.WINDOWS_SIZE
        #
        # # move camera UP in world space (so map scrolls down)
        # self.camera_y -= self.map_scroll_speed_per_frame
        #
        # # clamp so we never scroll past top or bottom of the map
        # max_camera_y = self.WORLD_HEIGHT - window_height
        # if max_camera_y < 0:
        #     max_camera_y = 0
        #
        # if self.camera_y < 0:
        #     self.camera_y = 0
        # elif self.camera_y > max_camera_y:
        #     self.camera_y = max_camera_y
        #
        # # keep Camera object in sync
        # self.camera.y = float(self.camera_y)

        # -------------------------------------------------------------
        # 🔥 ADDED: ENEMY UPDATE + ENEMY SHOOTING
        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # 🔥 UPDATE KAMIKAZE DRONES
        # -------------------------------------------------------------
        for drone in list(self.kamikazeDroneGroup):
            drone.update()

            if drone.enemyHealth <= 0:
                self.kamikazeDroneGroup.remove(drone)
                continue
        # for drone in list(self.kamikazeDroneGroup):
        #     drone.update()
        #
        #     # remove drone when health reaches zero
        #     if drone.enemyHealth <= 0:
        #         self.kamikazeDroneGroup.remove(drone)
        #         continue
        #
        #     # collision with player (kamikaze impact)
        #     if self.starship.hitbox.colliderect(drone.hitbox):
        #         self.starship.shipHealth -= drone.explosion_damage
        #         drone.enemyHealth = 0  # force removal next frame
        #         if drone in self.kamikazeDroneGroup:
        #             self.kamikazeDroneGroup.remove(drone)

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

            # print(f"[ROW CHECK] Player row={player_row} | Enemy row={enemy_row}")
            # print(f"[Y PIXEL] Player Y={self.starship.y} | Enemy Y={first_enemy.y}")

        # print(f"[ROW CHECK] Player row={player_row} | Enemy row={enemy_row}")
        # print(f"[Y PIXEL] Player Y={self.starship.y} | Enemy Y={enemy.y}")

        # if player_row == enemy_row:
        #     print(f"🔥 MATCH! Player and enemy are on SAME Y ROW at row={player_row}")
        # 🔥 HAZARD TILE COLLISION
        # HAZARD TILE COLLISION (WORLD → WORLD, CORRECT)
        hazard_layer = self.tiled_map.get_layer_by_name("hazard")
        player_rect = self.starship.hitbox  # already in WORLD coordinates

        for col, row, tile in hazard_layer.tiles():

            tile_rect = pygame.Rect(
                col * self.tile_size,
                row * self.tile_size,
                self.tile_size,
                self.tile_size
            )

            if player_rect.colliderect(tile_rect):
                self.starship.shipHealth -= 1
                print("⚠️ Player took hazard damage! Health =", self.starship.shipHealth)
                break


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

        # --- 3. Draw the PLAYER on top of everything else ---
        # --- 3. Draw the PLAYER on top of everything else ---
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)

        # --- 4. Draw enemies using their sprite method ---
        for enemy in self.bileSpitterGroup:
            enemy.draw(state.DISPLAY, self.camera)

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.draw(state.DISPLAY, self.camera)

        for drone in self.kamikazeDroneGroup:
            drone.draw(state.DISPLAY, self.camera)

        # --- 5. Draw bullets (world → screen) ---
        for bullet in self.player_bullets:
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * zoom)
            bh = int(bullet.height * zoom)
            rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(state.DISPLAY, (128, 0, 128), rect)
            # bullet hitbox debug
            hb_x = bx
            hb_y = by
            hb_w = bw
            hb_h = bh
            pygame.draw.rect(state.DISPLAY, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 1)

        for bullet in self.enemy_bullets:
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * zoom)
            bh = int(bullet.height * zoom)

            # Draw bullet
            rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(state.DISPLAY, bullet.color, rect)

            # 🔶 Draw hitbox (debug)
            pygame.draw.rect(
                state.DISPLAY,
                (255, 255, 0),  # yellow hitbox
                (bx, by, bw, bh),
                3  # thin line
            )


        # --- 6. Debug: enemy hitboxes ---
        for enemy_tri_spitter in self.triSpitterGroup:
            hb = pygame.Rect(
                self.camera.world_to_screen_x(enemy_tri_spitter.hitbox.x),
                self.camera.world_to_screen_y(enemy_tri_spitter.hitbox.y),
                int(enemy_tri_spitter.hitbox.width * zoom),
                int(enemy_tri_spitter.hitbox.height * zoom)
            )
            pygame.draw.rect(state.DISPLAY, (255, 255, 0), hb, 2)


        # --- 6. Debug: enemy hitboxes ---
        # --- Draw TRI SPITTER enemies (world → screen conversion) ---
        # for enemy_tri_spitter in self.triSpitterGroup:
        #     sx = self.camera.world_to_screen_x(enemy_tri_spitter.x)
        #     sy = self.camera.world_to_screen_y(enemy_tri_spitter.y)
        #
        #     # scale width/height if needed
        #     w = int(enemy_tri_spitter.width * self.camera.zoom)
        #     h = int(enemy_tri_spitter.height * self.camera.zoom)
        #
        #     # draw hitbox or sprite
        #     if hasattr(enemy_tri_spitter, "sprite") and enemy_tri_spitter.sprite:
        #         scaled = pygame.transform.scale(enemy_tri_spitter.sprite, (w, h))
        #         state.DISPLAY.blit(scaled, (sx, sy))
        #     else:
        #         # fallback: draw colored rectangle
        #         pygame.draw.rect(state.DISPLAY, enemy.color, pygame.Rect(sx, sy, w, h))

        # --- 4b. Draw kamikaze drones ---


        pygame.display.flip()


    def draw_tiled_background(self, surface: Surface) -> None:
        tile_size = self.tile_size
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        bg_layer = self.tiled_map.get_layer_by_name("background")

        for col, row, image in bg_layer.tiles():
            world_x = col * tile_size
            world_y = row * tile_size

            # only apply vertical camera offset, NO zoom here
            screen_x = world_x
            screen_y = world_y - self.camera_y

            # cull off-screen tiles
            if screen_y + tile_size < 0 or screen_y > window_height:
                continue

            surface.blit(image, (screen_x, screen_y))

            # -----------------------------
            # Draw HAZARD layer
            # -----------------------------
        hazard_layer = self.tiled_map.get_layer_by_name("hazard")

        for col, row, image in hazard_layer.tiles():
            world_x = col * tile_size
            world_y = row * tile_size

            screen_x = world_x
            screen_y = world_y - self.camera_y

            if screen_y + tile_size < 0 or screen_y > window_height:
                continue

            surface.blit(image, (screen_x, screen_y))

    def draw_background(self, surface: Surface) -> None:
        # use the tiled background instead of bands
        self.draw_tiled_background(surface)

    def load_enemy_into_list(self):
        print("LOAD BILE SPITTERS FUNCTION RAN!")

        for obj in self.tiled_map.objects:
            # ⭐ LOAD ENEMIES (existing code)
            if obj.name  == "bile_spitter":
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




