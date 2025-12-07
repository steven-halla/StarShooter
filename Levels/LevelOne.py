import pygame
import pytmx
from pygame import Surface

from Constants.GlobalConstants import GlobalConstants
from Entity.Monsters.BileSpitter import BileSpitter
from ScreenClasses.Camera import Camera
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelOne(VerticalBattleScreen):
    def __init__(self):
        super().__init__()
        print("LEVEL ONE INIT EXECUTED")

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
        self.map_scroll_speed_per_frame: float = .1

        self.bileSpitterGroup: list[BileSpitter] = []

        self.load_bile_spitters()

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
        if player_x is None or player_y is None:
            print("ERROR: No 'player' object found in Tiled map!")
            player_x = 300
            player_y = 355

        # APPLY PLAYER POSITION
        self.starship.x = player_x
        self.starship.y = player_y

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

        # super().update(state)

        # now handle map scroll ONLY in LevelOne
        _, window_height = GlobalConstants.WINDOWS_SIZE

        # move camera UP in world space (so map scrolls down)
        self.camera_y -= self.map_scroll_speed_per_frame

        # clamp so we never scroll past top or bottom of the map
        max_camera_y = self.WORLD_HEIGHT - window_height
        if max_camera_y < 0:
            max_camera_y = 0

        if self.camera_y < 0:
            self.camera_y = 0
        elif self.camera_y > max_camera_y:
            self.camera_y = max_camera_y

        # keep Camera object in sync
        self.camera.y = float(self.camera_y)

        # -------------------------------------------------------------
        # 🔥 ADDED: ENEMY UPDATE + ENEMY SHOOTING
        # -------------------------------------------------------------
        for enemy in self.bileSpitterGroup:
            enemy.update()
            # print("PLAYER HITBOX:", self.starship.hitbox)
            # print("ENEMY HITBOX:", enemy.hitbox)
            if self.starship.hitbox.colliderect(enemy.hitbox):
                print("jf;dlajflsa")
                enemy.color = (135, 206, 235)  # SKYBLUE
            else:

                enemy.color = GlobalConstants.RED
            enemy.update_hitbox()

            if enemy.enemyBullets:  # enemy fired bullets
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

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
        enemy_row = int(enemy.y // tile_h)

        print(f"[ROW CHECK] Player row={player_row} | Enemy row={enemy_row}")
        print(f"[Y PIXEL] Player Y={self.starship.y} | Enemy Y={enemy.y}")

        if player_row == enemy_row:
            print(f"🔥 MATCH! Player and enemy are on SAME Y ROW at row={player_row}")






    def draw(self, state):
        super().draw(state)
        # Draw ONLY the background layer from the tilemap
        # if "background" in self.tiled_map.layernames:
        #     bg_layer = self.tiled_map.get_layer_by_name("background")
        #
        #     tile_w = self.tiled_map.tilewidth
        #     tile_h = self.tiled_map.tileheight
        #
        #     for x, y, gid in bg_layer:
        #         tile = self.tiled_map.get_tile_image_by_gid(gid)
        #         if tile:
        #             world_x = x * tile_w
        #             world_y = y * tile_h
        #
        #             screen_x = self.camera.world_to_screen_x(world_x)
        #             screen_y = self.camera.world_to_screen_y(world_y)
        #
        #             state.DISPLAY.blit(tile, (screen_x, screen_y))
        # for layer in self.tiled_map.visible_layers:
        #     if isinstance(layer, pytmx.TiledTileLayer):
        #         for x, y, gid in layer:
        #             tile = self.tiled_map.get_tile_image_by_gid(gid)
        #             if tile:
        #                 world_x = x * self.tiled_map.tilewidth
        #                 world_y = y * self.tiled_map.tileheight
        #                 screen_x = self.camera.world_to_screen_x(world_x)
        #                 screen_y = self.camera.world_to_screen_y(world_y)
        #                 state.DISPLAY.blit(tile, (screen_x, screen_y))

            # Draw objects (like player, shops, etc.)
        for obj in self.tiled_map.objects:
            if hasattr(obj, "image") and obj.image:
                screen_x = self.camera.world_to_screen_x(obj.x)
                screen_y = self.camera.world_to_screen_y(obj.y)
                state.DISPLAY.blit(obj.image, (screen_x, screen_y))

        # self.draw_tiled_background(state)

        # if not self.playerDead:
        #     self.starship.draw(state.DISPLAY)

        # if not self.playerDead:
        #     zoom = self.camera.zoom
        #
        #     ship_screen_x = self.camera.world_to_screen_x(self.starship.x)
        #     ship_screen_y = self.camera.world_to_screen_y(self.starship.y)
        #
        #     ship_width = int(self.starship.width * zoom)
        #     ship_height = int(self.starship.height * zoom)
        #
        #     ship_rect = pygame.Rect(
        #         ship_screen_x,
        #         ship_screen_y,
        #         ship_width,
        #         ship_height,
        #     )
        #     pygame.draw.rect(state.DISPLAY, self.starship.color, ship_rect)

        # enemies
        for enemy in self.bileSpitterGroup:
            zoom = self.camera.zoom
            enemy_x = self.camera.world_to_screen_x(enemy.x)
            enemy_y = self.camera.world_to_screen_y(enemy.y)
            enemy_w = int(enemy.width * zoom)
            enemy_h = int(enemy.height * zoom)
            rect = pygame.Rect(enemy_x, enemy_y, enemy_w, enemy_h)
            pygame.draw.rect(state.DISPLAY, enemy.color, rect)

        # bullets
        for bullet in self.player_bullets:
            zoom = self.camera.zoom
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * zoom)
            bh = int(bullet.height * zoom)
            rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(state.DISPLAY, (128, 0, 128), rect)

        for bullet in self.enemy_bullets:
            zoom = self.camera.zoom
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * zoom)
            bh = int(bullet.height * zoom)
            rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(state.DISPLAY, bullet.color, rect)

        # DEBUG: draw enemy hitboxes correctly
        zoom = self.camera.zoom
        for enemy in self.bileSpitterGroup:
            hb = pygame.Rect(
                self.camera.world_to_screen_x(enemy.hitbox.x),
                self.camera.world_to_screen_y(enemy.hitbox.y),
                int(enemy.hitbox.width * zoom),
                int(enemy.hitbox.height * zoom)
            )
            pygame.draw.rect(state.DISPLAY, (255, 255, 0), hb, 2)

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

    def draw_background(self, surface: Surface) -> None:
        # use the tiled background instead of bands
        self.draw_tiled_background(surface)

    def load_bile_spitters(self):
        print("LOAD BILE SPITTERS FUNCTION RAN!")

        for obj in self.tiled_map.objects:
            print("--- OBJECT FOUND:", obj.name, obj.type, obj.x, obj.y)

            # ⭐ LOAD PLAYER FROM TILED
            if obj.name == "player":
                print(">>> PLAYER FOUND IN TILED <<<")
                self.starship.x = obj.x
                self.starship.y = obj.y
                continue  # don't treat player as enemy

            # ⭐ LOAD ENEMIES (existing code)
            if obj.properties.get("Type") == "bile_spitter":
                enemy = BileSpitter()
                enemy.x = obj.x
                enemy.y = obj.y

                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()

                self.bileSpitterGroup.append(enemy)

        print("Bile spitter count =", len(self.bileSpitterGroup))
        print(f"Player loaded at X={self.starship.x}, Y={self.starship.y}")
