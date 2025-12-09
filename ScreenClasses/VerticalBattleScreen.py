import pygame
from pygame import Surface
import pytmx

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Controller.KeyBoardControls import KeyBoardControls
from Entity.StarShip import StarShip
from Movement.MoveRectangle import MoveRectangle
from ScreenClasses.Camera import Camera
from Weapons.Bullet import Bullet


class VerticalBattleScreen:
    def __init__(self):
        self.starship: StarShip = StarShip()
        # self.isStart: bool = True
        self.playerDead: bool = False
        self.tiled_map = pytmx.load_pygame("")
        self.tile_size: int = self.tiled_map.tileheight



        self.mover: MoveRectangle = MoveRectangle()
        self.controller: KeyBoardControls = KeyBoardControls()

        self.STARSHIP_HORIZONTAL_CENTER_DIVISOR: int = 2
        self.STARSHIP_BOTTOM_OFFSET: int = 100
        self.MIN_X: int = 0
        self.MIN_Y: int = 0
        self.map_scroll_speed_per_frame: float = 4334.33


        self.was_q_pressed_last_frame: bool = False

        self.player_bullets: list = []
        self.enemy_bullets: list = []     # LevelOne can append to this list

        self.WORLD_HEIGHT: int = GlobalConstants.WINDOWS_SIZE[1] * 3

        self.SCROLL_SPEED_PER_SECOND: float = 55.0
        self.camera_y: float = 0.0
        self.SCROLL_SPEED_PER_FRAME: float = 55.0

        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        self.window_width = window_width
        self.window_height = window_height

        self.camera = Camera(
            window_width=window_width,
            window_height=window_height,
            world_height=self.WORLD_HEIGHT,
            scroll_speed_per_frame=self.SCROLL_SPEED_PER_FRAME,
            initial_zoom=2.0,   # DO NOT TOUCH CAMERA SETTINGS
        )


    def start(self, state):
        pass


    def clamp_starship_to_screen(self):
        zoom = self.camera.zoom
        ship_w = self.starship.width
        ship_h = self.starship.height

        # --- HORIZONTAL (NO CAMERA X), EASY ---
        max_x = self.window_width / zoom - ship_w
        if self.starship.x < 0:
            self.starship.x = 0
        elif self.starship.x > max_x:
            self.starship.x = max_x

        # --- VERTICAL (CAMERA Y ACTIVE) ---
        cam_y = self.camera.y
        win_h = self.window_height

        min_y = cam_y
        max_y = cam_y + (win_h / zoom) - ship_h

        if self.starship.y < min_y:
            self.starship.y = min_y
        elif self.starship.y > max_y:
            self.starship.y = max_y

    def move_map_y_axis(self):
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

    def update(self, state):
        # print("PLAYER UPDATE Y:", self.starship.y)
        # print("STARSHIP INSTANCE:", id(self.starship))
        # now handle map scroll ONLY in LevelOne
        self.move_map_y_axis()


        if not hasattr(self, "start_has_run"):
            self.start(state)  # This calls LevelOne.start()
            self.start_has_run = True
        # self.starship.update()
        if self.starship.shipHealth <= 0:
            self.playerDead = True
        #
        # if self.isStart:
        #     self.start(state)
        #     self.isStart = False

        self.controller.update()

        # Player movement
        if not self.playerDead:
            if self.controller.left_button:
                self.mover.player_move_left(self.starship)
            if self.controller.right_button:
                self.mover.player_move_right(self.starship)
            if self.controller.up_button:
                self.mover.player_move_up(self.starship)
            if self.controller.down_button:
                self.mover.player_move_down(self.starship)
        self.starship.update()

        self.was_q_pressed_last_frame = self.controller.q_button

        self.clamp_starship_to_screen()
        # if not self.playerDead:
        #     self.starship.update()

        # -------------------------
        # PLAYER SHOOTING ONLY
        # -------------------------
        if (
            self.controller.main_weapon_button
            and self.starship.bullet_timer.is_ready()
            and not self.playerDead
        ):
            center_x = self.starship.x + self.starship.width // 2 + 14
            bullet_y = self.starship.y

            spread = self.starship.bullet_spread_offset
            count = self.starship.bullets_per_shot
            start_index = -(count // 2)

            for i in range(count):
                offset = (start_index + i) * spread
                bullet_x = center_x + offset - Bullet.DEFAULT_WIDTH // 2
                # self.player_bullets.append(Bullet(bullet_x, bullet_y))
                bullet_world_x = bullet_x
                bullet_world_y = bullet_y

                self.player_bullets.append(Bullet(bullet_world_x, bullet_world_y))
                # print(f"SHIP WORLD POS: ({self.starship.x}, {self.starship.y})")
                # print(f"BULLET SPAWN POS: ({bullet_x}, {bullet_y})")

            self.starship.bullet_timer.reset()

        for bullet in list(self.player_bullets):
            bullet.update()

            # Convert to screen space
            screen_y = bullet.y - self.camera.y

            # If bullet is above the visible screen area → delete
            if screen_y + bullet.height < 0:
                # print(f"[DELETE] Bullet removed at world_y={bullet.y}, screen_y={screen_y}")
                self.player_bullets.remove(bullet)




        # -------------------------
        # ENEMY BULLETS ONLY
        # -------------------------
        screen_top = self.camera.y
        screen_bottom = self.camera.y + (self.window_height / self.camera.zoom)
        for bullet in list(self.enemy_bullets):
            bullet.update()

            # WORLD-SPACE BOUNDS (same logic as player bullets)
            world_top_delete = self.camera.y - 200
            world_bottom_delete = self.camera.y + self.window_height + 200

            if bullet.y < world_top_delete or bullet.y > world_bottom_delete:
                print(f"[DELETE ENEMY] y={bullet.y}, cam_y={self.camera.y}")
                self.enemy_bullets.remove(bullet)
                continue

            # Collision check
            if bullet.collide_with_rect(self.starship.hitbox):
                self.starship.shipHealth -= bullet.damage
                bullet.is_active = False
                self.enemy_bullets.remove(bullet)

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



    def draw(self, state) -> None:

        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        zoom = self.camera.zoom

        scene_surface = pygame.Surface((window_width, window_height))

        self.draw_tiled_background(scene_surface)

        scaled_scene = pygame.transform.scale(
            scene_surface,
            (int(window_width * zoom), int(window_height * zoom))
        )

        state.DISPLAY.fill(GlobalConstants.BLACK)
        state.DISPLAY.blit(scaled_scene, (0, 0))




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



