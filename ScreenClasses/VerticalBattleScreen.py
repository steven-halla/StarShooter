import pygame
from pygame import Surface

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

        self.mover: MoveRectangle = MoveRectangle()
        self.controller: KeyBoardControls = KeyBoardControls()

        self.STARSHIP_HORIZONTAL_CENTER_DIVISOR: int = 2
        self.STARSHIP_BOTTOM_OFFSET: int = 100
        self.MIN_X: int = 0
        self.MIN_Y: int = 0

        self.was_q_pressed_last_frame: bool = False

        self.player_bullets: list = []
        self.enemy_bullets: list = []     # LevelOne can append to this list

        self.WORLD_HEIGHT: int = GlobalConstants.WINDOWS_SIZE[1] * 3

        self.SCROLL_SPEED_PER_SECOND: float = 100.0
        self.camera_y: float = 0.0
        self.SCROLL_SPEED_PER_FRAME: float = 111.0

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
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        # self.starship.x = window_width // self.STARSHIP_HORIZONTAL_CENTER_DIVISOR
        # self.starship.y = window_height - self.STARSHIP_BOTTOM_OFFSET

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

    def update(self, state):
        # print("PLAYER UPDATE Y:", self.starship.y)
        # print("STARSHIP INSTANCE:", id(self.starship))

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

        # Update player bullets
        # for bullet in list(self.player_bullets):
        #     bullet.update()
        #     if bullet.y + bullet.height < 0:
        #         self.player_bullets.remove(bullet)
        # Update player bullets
        # Update player bullets
        for bullet in list(self.player_bullets):
            bullet.update()

            # Convert to screen space
            screen_y = bullet.y - self.camera.y

            # If bullet is above the visible screen area → delete
            if screen_y + bullet.height < 0:
                print(f"[DELETE] Bullet removed at world_y={bullet.y}, screen_y={screen_y}")
                self.player_bullets.remove(bullet)

        # AFTER updating everything — print all bullets still alive
        print("[PLAYER BULLETS IN ARRAY]:")
        for i, bullet in enumerate(self.player_bullets):
            print(f"   #{i}: x={bullet.x:.2f}, y={bullet.y:.2f}")


        # -------------------------
        # ENEMY BULLETS ONLY
        # (LevelOne puts bullets into self.enemy_bullets)
        # -------------------------
        # -------------------------
        # ENEMY BULLETS ONLY
        # -------------------------
        screen_top = self.camera.y
        screen_bottom = self.camera.y + (self.window_height / self.camera.zoom)

        for bullet in list(self.enemy_bullets):
            bullet.update()

            # delete only when bullet leaves visible WORLD range
            if bullet.y < screen_top or bullet.y > screen_bottom:
                self.enemy_bullets.remove(bullet)
                continue

            if bullet.collide_with_rect(self.starship.hitbox):
                self.starship.shipHealth -= bullet.damage
                bullet.is_active = False
                self.enemy_bullets.remove(bullet)
        # _, window_height = GlobalConstants.WINDOWS_SIZE
        #
        # for bullet in list(self.enemy_bullets):
        #     bullet.update()
        #
        #     if bullet.y > window_height:
        #         self.enemy_bullets.remove(bullet)
        #         continue
        #
        #     if bullet.collide_with_rect(self.starship.hitbox):
        #         self.starship.shipHealth -= bullet.damage
        #         self.starship.on_hit()
        #         if not bullet.is_active:
        #             self.enemy_bullets.remove(bullet)

    def draw(self, state) -> None:

        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        zoom = self.camera.zoom

        scene_surface = pygame.Surface((window_width, window_height))

        # Background FIRST
        self.draw_background(scene_surface)

        # Starship SECOND (only sliced sprite)
        # if not self.playerDead:
        #     self.starship.draw(scene_surface, self.camera)
        # Bullets
        # for bullet in self.player_bullets:
        #     bullet.draw(scene_surface)
        #
        # for bullet in self.enemy_bullets:
        #     bullet.draw(scene_surface)

        # Scale + present
        scaled_scene = pygame.transform.scale(
            scene_surface,
            (int(window_width * zoom), int(window_height * zoom))
        )

        state.DISPLAY.fill(GlobalConstants.BLACK)
        state.DISPLAY.blit(scaled_scene, (0, 0))

    # def draw(self, state) -> None:
    #     window_width, window_height = GlobalConstants.WINDOWS_SIZE
    #     zoom = self.camera.zoom
    #
    #     scene_surface = pygame.Surface((window_width, window_height))
    #
    #     self.draw_background(scene_surface)
    #
    #     if not self.playerDead:
    #         self.starship.draw(scene_surface)
    #
    #     # LevelOne draws enemies — not this class.
    #
    #     for bullet in self.player_bullets:
    #         bullet.draw(scene_surface)
    #
    #     for bullet in self.enemy_bullets:
    #         bullet.draw(scene_surface)
    #
    #     scaled_scene = pygame.transform.scale(
    #         scene_surface,
    #         (int(window_width * zoom), int(window_height * zoom))
    #     )
    #
    #     state.DISPLAY.fill(GlobalConstants.BLACK)
    #     state.DISPLAY.blit(scaled_scene, (0, 0))


    def draw_background(self, surface: Surface) -> None:
        self.draw_scrolling_background(surface)


    def draw_scrolling_background(self, surface: "Surface") -> None:
        # Your scrolling band background unchanged
        pass
