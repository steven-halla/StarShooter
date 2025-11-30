import pygame
from pygame import Surface

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Controller.KeyBoardControls import KeyBoardControls
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.StarShip import StarShip
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class VerticalBattleScreen:
    def __init__(self):
        self.starship: StarShip = StarShip()
        self.isStart: bool = True
        self.mover: MoveRectangle = MoveRectangle()
        self.controller: KeyBoardControls = KeyBoardControls()
        self.STARSHIP_HORIZONTAL_CENTER_DIVISOR: int = 2
        self.STARSHIP_BOTTOM_OFFSET: int = 100
        self.MIN_X: int = 0
        self.MIN_Y: int = 0
        self.scrollScreen: bool = False
        self.bileSpitterGroup: list[BileSpitter] = []

        self.bile_spitter: BileSpitter = BileSpitter()
        self.ENEMY_HORIZONTAL_CENTER_DIVISOR: int = 2
        self.ENEMY_TOP_OFFSET: int = 50
        self.was_q_pressed_last_frame: bool = False

        self.player_bullets: list = []
        self.enemy_bullets: list = []   # Bullet objects ONLY

        self.WORLD_HEIGHT: int = GlobalConstants.WINDOWS_SIZE[1] * 3  # 3 screens tall
        self.SCROLL_SPEED_PER_SECOND: float = 100.0
        self.camera_y: float = 0.0

        self.BAND_COLORS: list[tuple[int, int, int]] = [
            GlobalConstants.PINK,
            GlobalConstants.GREY,
            GlobalConstants.BLACK,
        ]

        self.WORLD_HEIGHT: int = GlobalConstants.WINDOWS_SIZE[1] * 3  # 3 screens tall

        # scrolling
        self.SCROLL_SPEED_PER_FRAME: float = 2.0  # same as: scroll_speed = 2.0
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        # start at the BOTTOM of the world
        self.camera_y: float = self.WORLD_HEIGHT - window_height
        self.playerDead: bool = False



    def start(self, state):
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        self.starship.x = window_width // self.STARSHIP_HORIZONTAL_CENTER_DIVISOR
        self.starship.y = window_height - self.STARSHIP_BOTTOM_OFFSET

        self.bile_spitter.x = window_width // self.ENEMY_HORIZONTAL_CENTER_DIVISOR
        self.bile_spitter.y = self.ENEMY_TOP_OFFSET

        if self.bile_spitter not in self.bileSpitterGroup:
            self.bileSpitterGroup.append(self.bile_spitter)

    def clamp_starship_to_screen(self) -> None:
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        max_x = window_width - self.starship.width
        max_y = window_height - self.starship.height

        if self.starship.x < self.MIN_X:
            self.starship.x = self.MIN_X

        elif self.starship.x > max_x:
            self.starship.x = max_x

        if self.starship.y < self.MIN_Y:
            self.starship.y = self.MIN_Y
        elif self.starship.y > max_y:
            self.starship.y = max_y

    def update(self, state):
        print(self.starship.shipHealth)
        if self.starship.shipHealth <= 0:
            self.playerDead = True
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        if self.isStart:
            self.start(state)
            self.isStart = False

        self.controller.update()

        if self.playerDead == False:
            if self.controller.left_button:
                self.mover.player_move_left(self.starship)
            if self.controller.right_button:
                self.mover.player_move_right(self.starship)
            if self.controller.up_button:
                self.mover.player_move_up(self.starship)
            if self.controller.down_button:
                self.mover.player_move_down(self.starship)

            if self.controller.q_button and not self.was_q_pressed_last_frame:
                # Q was just pressed this frame
                self.scrollScreen = not self.scrollScreen

        # remember Q state for next frame
        self.was_q_pressed_last_frame = self.controller.q_button

        # --- scroll while scrollScreen is True ---
        if self.scrollScreen:
            self.update_camera_scroll(state)


        self.clamp_starship_to_screen()
        if self.playerDead == False:
            self.starship.update()

        self.starship.update()



        # NEED weapon types later on
        # NEED weapon types later on
        if self.controller.main_weapon_button and self.starship.bullet_timer.is_ready() and self.playerDead == False:
            center_x = self.starship.x + self.starship.width // 2 + 14
            bullet_y = self.starship.y

            spread = self.starship.bullet_spread_offset
            count = self.starship.bullets_per_shot
            start_index = -(count // 2)

            for i in range(count):
                offset = (start_index + i) * spread
                bullet_x = center_x + offset - Bullet.DEFAULT_WIDTH // 2

                new_bullet = Bullet(bullet_x, bullet_y)
                self.player_bullets.append(new_bullet)

            print(f"player_bullets count = {len(self.player_bullets)}")

            # VERY IMPORTANT: reset the timer after firing
            self.starship.bullet_timer.reset()
        # if self.controller.main_weapon_button:
        #     bullet_x = (
        #         self.starship.x
        #         + self.starship.width // 2
        #         - Bullet.DEFAULT_WIDTH // 2
        #     )
        #     bullet_y = self.starship.y
        #
        #     new_bullet = Bullet(bullet_x, bullet_y)
        #     self.player_bullets.append(new_bullet)
        #
        #     for bullet in list(self.player_bullets):
        #         bullet.update()
        #         if bullet.y + bullet.height < 0:
        #             self.player_bullets.remove(bullet)
        #
        #     print(f"player_bullets count = {len(self.player_bullets)}")


        for bullet in self.player_bullets:
            bullet.update()
            if bullet.y + bullet.height < 0:
                self.player_bullets.remove(bullet)


                # remove bullet after hit IF you want
                # self.enemy_bullets.remove(bullet)
        # print("player_bullets count =", len(self.player_bullets))

        # -------------------------
        # ENEMY SHOOTING (FIXED)
        # -------------------------
        # self.bile_spitter.update()
        for enemy in self.bileSpitterGroup:
            enemy.update()

        # Transfer NEW enemy bullets to the battle screen
        if self.bile_spitter.enemyBullets:
            self.enemy_bullets.extend(self.bile_spitter.enemyBullets)
            self.bile_spitter.enemyBullets.clear()

        # # --- PLAYER BULLETS ---
        # for bullet in list(self.player_bullets):
        #
        #     bullet.update()  # FIRST move the bullet
        #
        #     # remove if offscreen
        #     if bullet.y + bullet.height < 0:
        #         self.player_bullets.remove(bullet)
        #         continue
        #
        #     # NOW collision works because bullet.rect is correct
        #     if self.bile_spitter.hitbox.colliderect(bullet.rect):
        #         print("HIT ENEMY!")
        #         self.bile_spitter.on_hit()
        #         self.player_bullets.remove(bullet)
        #         continue
        # --- PLAYER BULLETS ---
        for bullet in list(self.player_bullets):
            # 1) move the bullet first
            bullet.update()

            # 2) remove if off the top of the screen
            if bullet.y + bullet.height < 0:
                self.player_bullets.remove(bullet)
                continue

            # 3) check collision against ALL bile spitters in the group
            hit_something = False

            for enemy in list(self.bileSpitterGroup):
                enemy.update_hitbox()
                if bullet.collide_with_rect(enemy.hitbox):
                    enemy.enemyHealth -= self.starship.bulletDamage
                    print("Enemy HP =", enemy.enemyHealth)

                    if not bullet.is_active:
                        self.player_bullets.remove(bullet)

                    if enemy.enemyHealth <= 0:
                        self.bileSpitterGroup.remove(enemy)
                    break  # stop checking this bullet vs other enemies

            if hit_something:
                continue

        # Update enemy bullets and remove off-screen
        # Update enemy bullets and remove off-screen
        for bullet in list(self.enemy_bullets):
            bullet.update()

            # 1) Off-screen cleanup
            if bullet.y > window_height:
                self.enemy_bullets.remove(bullet)
                continue

            # 2) Collision with player
            if bullet.collide_with_rect(self.starship.hitbox):
                # apply damage
                self.starship.shipHealth -= bullet.damage
                print(f"Ship HP = {self.starship.shipHealth}")

                # color / hit reaction
                self.starship.on_hit()

                # if bullet deactivates itself, also yank it from the list
                if not bullet.is_active:
                    self.enemy_bullets.remove(bullet)
                continue
        # ...after bullets / enemy updates
        # inside update(...), AFTER self.controller.update()




    def draw(self, state):
        # state.DISPLAY.fill(GlobalConstants.BLACK)
        self.draw_scrolling_background(state.DISPLAY)

        if self.playerDead == False:
            self.starship.draw(state.DISPLAY)
        # self.bile_spitter.draw(state.DISPLAY)
        for enemy in self.bileSpitterGroup:
            enemy.draw(state.DISPLAY)

        # draw player bullets
        for bullet in self.player_bullets:
            bullet.draw(state.DISPLAY)

        # draw enemy bullets
        for bullet in self.enemy_bullets:
            bullet.draw(state.DISPLAY)

        pygame.display.flip()

    def update_camera_scroll(self, state) -> None:
        _, window_height = GlobalConstants.WINDOWS_SIZE

        max_camera_y: float = self.WORLD_HEIGHT - window_height
        min_camera_y: float = 0.0

        # move camera UP in world space (so you fly “up” the map),
        # but don’t go past the top
        self.camera_y = max(min_camera_y, self.camera_y - self.SCROLL_SPEED_PER_FRAME)

    def draw_scrolling_background(self, surface: "Surface") -> None:
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        top_world_y: float = self.camera_y
        bottom_world_y: float = self.camera_y + window_height

        band_height: float = window_height  # each band is one screen tall

        for index, color in enumerate(self.BAND_COLORS):
            band_top: float = index * band_height
            band_bottom: float = band_top + band_height

            visible_top: float = max(band_top, top_world_y)
            visible_bottom: float = min(band_bottom, bottom_world_y)

            if visible_bottom <= visible_top:
                continue

            screen_y: float = visible_top - top_world_y
            rect_height: float = visible_bottom - visible_top

            pygame.draw.rect(
                surface,
                color,
                pygame.Rect(0, int(screen_y), window_width, int(rect_height)),
            )
