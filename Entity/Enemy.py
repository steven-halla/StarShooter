import math
import pygame
from Constants.GlobalConstants import GlobalConstants
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class Enemy:
    def __init__(self):
        # size
        self.width: int = 0
        self.height: int = 0
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20
        # generic bullet config (base enemy default)
        self.bullet_speed: float = 0.0
        self.bullet_damage: int = 10

        # No longer using self.enemyBullets - using game_state.enemy_bullets instead



        # position (WORLD space)
        self.x: float = 0
        self.y: float = 0

        # movement
        self.moveSpeed: float = 0.0
        self.mover: MoveRectangle = MoveRectangle()

        # combat / stats
        self.enemyHealth: int = 0
        self.last_enemy_health: int = self.enemyHealth

        self.exp: int = 0
        self.credits: int = 0

        # rendering / damage flash
        self.is_flashing: bool = False
        self.flash_start_time: int = 0
        self.flash_duration_ms: int = 120
        self.flash_interval_ms: int = 30

        # references (set by level)
        self.camera = None
        self.target_player = None

        # collision
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

        # state flags
        self.is_on_screen: bool = False
        self.has_entered_screen: bool = False
        self.is_active: bool = False
        self.enemy_list: list[Enemy] = []

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update(self, state):
        self.update_hitbox()

        if self.camera is None:
            self.is_active = False
            return

        self.clamp_horizontal()
        self.is_on_screen = self.mover.enemy_on_screen(self, self.camera)

        if self.is_on_screen and self.player_in_vicinity():
            self.is_active = True
            self.has_entered_screen = True
            self.clamp_vertical()
        else:
            self.is_active = False

        # 🔑 DAMAGE DETECTION (THIS IS THE KEY)
        if self.enemyHealth < self.last_enemy_health:
            self.is_flashing = True
            self.flash_start_time = pygame.time.get_ticks()

        self.last_enemy_health = self.enemyHealth

        # 🔑 FLASH TIMER
        if self.is_flashing:
            if pygame.time.get_ticks() - self.flash_start_time >= self.flash_duration_ms:
                self.is_flashing = False


    # --------------------------------------------------
    # DAMAGE
    # --------------------------------------------------
    def take_damage(self, amount: int) -> None:
        self.enemyHealth -= amount
        self.is_flashing = True
        self.flash_start_time = pygame.time.get_ticks()

    # --------------------------------------------------
    # DRAW DAMAGE FLASH (CALLED AFTER CHILD DRAW)
    # --------------------------------------------------
    def draw(self, surface: pygame.Surface, camera) -> None:
        # Don't draw if not active (e.g., removed due to collision with UI panel)
        if not self.is_active:
            return

        if not self.is_flashing:
            return

        elapsed = pygame.time.get_ticks() - self.flash_start_time
        if elapsed >= self.flash_duration_ms:
            self.is_flashing = False
            return

        # blink timing
        if (elapsed // self.flash_interval_ms) % 2 != 0:
            return

        x = camera.world_to_screen_x(self.hitbox.x)
        y = camera.world_to_screen_y(self.hitbox.y)
        w = int(self.hitbox.width * camera.zoom)
        h = int(self.hitbox.height * camera.zoom)

        flash = pygame.Surface((w, h), pygame.SRCALPHA)
        flash.fill((*GlobalConstants.RED, 160))
        surface.blit(flash, (x, y))

    # --------------------------------------------------
    # CLAMPING
    # --------------------------------------------------
    def clamp_horizontal(self) -> None:
        max_x = (self.camera.window_width / self.camera.zoom) - self.width
        self.x = max(0, min(self.x, max_x))

    def clamp_vertical(self) -> None:
        cam_top = self.camera.y
        cam_bottom = (
            self.camera.y
            + (self.camera.window_height / self.camera.zoom)
            - self.height
        )
        self.y = max(cam_top, min(self.y, cam_bottom))

    # --------------------------------------------------
    # PROXIMITY
    # --------------------------------------------------
    def player_in_vicinity(self) -> bool:
        if self.camera is None or self.target_player is None:
            return False

        dx = abs(self.x - self.target_player.x)
        dy = abs(self.y - self.target_player.y)
        return dx <= 400 and dy <= 300

    # --------------------------------------------------
    # HITBOX
    # --------------------------------------------------
    def update_hitbox(self) -> None:
        self.hitbox.update(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height),
        )

    def draw_damage_flash(self, surface: pygame.Surface, camera) -> None:
        # Don't draw if not active (e.g., removed due to collision with UI panel)
        if not self.is_active:
            return

        if not self.is_flashing:
            return

        elapsed = pygame.time.get_ticks() - self.flash_start_time
        if elapsed >= self.flash_duration_ms:
            self.is_flashing = False
            return

        if (elapsed // self.flash_interval_ms) % 2 != 0:
            return

        x = camera.world_to_screen_x(self.hitbox.x)
        y = camera.world_to_screen_y(self.hitbox.y)
        w = int(self.hitbox.width * camera.zoom)
        h = int(self.hitbox.height * camera.zoom)

        flash = pygame.Surface((w, h), pygame.SRCALPHA)
        flash.fill((*GlobalConstants.RED, 160))
        surface.blit(flash, (x, y))

    # the below  is attacks from boss level 6, need to do this better
    def draw_barrage(self, *args):
        pass

    def apply_barrage_damage(self, *args):
        pass

    def shoot_single_down_vertical_y(
            self,
            bullet_speed: float,
            bullet_width: int,
            bullet_height: int,
            bullet_color: tuple[int, int, int],
            bullet_damage: int,
            state
    ) -> None:
        bullet_x = self.x + self.width // 2 - bullet_width // 2
        bullet_y = self.y + self.height

        bullet = Bullet(bullet_x, bullet_y)
        bullet.color = bullet_color
        bullet.width = bullet_width
        bullet.height = bullet_height
        bullet.damage = bullet_damage

        bullet.vx = 0
        bullet.vy = 1
        bullet.bullet_speed = bullet_speed

        bullet.update_rect()
        state.enemy_bullets.append(bullet)

        #how to call for single shot
        # self.shoot_single_down_vertical_y(
        #     bullet_speed=4.0,
        #     bullet_width=20,
        #     bullet_height=20,
        #     bullet_color=self.bulletColor,
        #     bullet_damage=10
        # )

    def shoot_multiple_down_vertical_y(
            self,
            bullet_speed: float,
            bullet_width: int,
            bullet_height: int,
            bullet_color: tuple[int, int, int],
            bullet_damage: int,
            bullet_count: int,
            bullet_spread: int,
            state
    ) -> None:
        start_x = self.x + self.width // 2 - bullet_width // 2
        bullet_y = self.y + self.height

        if bullet_count <= 1:
            offsets = [0]
        else:
            half = (bullet_count - 1) / 2
            offsets = [int((i - half) * bullet_spread) for i in range(bullet_count)]

        for offset in offsets:
            bullet = Bullet(start_x + offset, bullet_y)
            bullet.color = bullet_color
            bullet.width = bullet_width
            bullet.height = bullet_height
            bullet.damage = bullet_damage

            bullet.vx = 0
            bullet.vy = 1
            bullet.bullet_speed = bullet_speed

            bullet.update_rect()
            state.enemy_bullets.append(bullet)
            # below is how to call this fun with 3 bullet spread
            # self.shoot_multiple_down_vertical_y(
            #     bullet_speed=4.0,
            #     bullet_width=20,
            #     bullet_height=20,
            #     bullet_color=self.bulletColor,
            #     bullet_damage=10,
            #     bullet_count=3,
            #     bullet_spread=44
            # )

    def shoot_spores(
            self,
            bullet_speed: float,
            bullet_width: int,
            bullet_height: int,
            bullet_color: tuple[int, int, int],
            bullet_damage: int,
            state
    ) -> None:
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        directions = [
            (-1, 0),  # LEFT
            (0, 1),  # DOWN
            (1, 0),  # RIGHT
            (0, -1),  # UP
            (-1, -1),  # UP-LEFT
            (1, -1),  # UP-RIGHT
            (-1, 1),  # DOWN-LEFT
            (1, 1),  # DOWN-RIGHT
        ]

        for dx, dy in directions:
            b = Bullet(cx, cy)
            b.width = bullet_width
            b.height = bullet_height
            b.color = bullet_color
            b.damage = bullet_damage

            b.vx = dx
            b.vy = dy
            b.bullet_speed = bullet_speed

            b.update_rect()
            state.enemy_bullets.append(b)
            # how to call
            # self.shoot_spores(
            #     bullet_speed=4.0,
            #     bullet_width=20,
            #     bullet_height=20,
            #     bullet_color=self.bulletColor,
            #     bullet_damage=10
            # )

    def shoot_single_bullet_aimed_at_player(
            self,
            bullet_speed: float,
            bullet_width: int,
            bullet_height: int,
            bullet_color: tuple[int, int, int],
            bullet_damage: int,
            state
    ) -> None:
        if self.target_player is None:
            return

        cam_top = self.camera.y
        cam_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        if self.y + self.height < cam_top or self.y > cam_bottom:
            return

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        px = self.target_player.hitbox.centerx
        py = self.target_player.hitbox.centery

        dx = px - cx
        dy = py - cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        dx /= dist
        dy /= dist

        bullet = Bullet(cx, cy)
        bullet.width = bullet_width
        bullet.height = bullet_height
        bullet.color = bullet_color
        bullet.damage = bullet_damage

        bullet.vx = dx
        bullet.vy = dy
        bullet.bullet_speed = bullet_speed

        bullet.update_rect()
        state.enemy_bullets.append(bullet)
        # how to call
        # self.shoot_single_bullet_aimed_at_player(
        #     bullet_speed=4.0,
        #     bullet_width=20,
        #     bullet_height=20,
        #     bullet_color=self.bulletColor,
        #     bullet_damage=10
        # )

    def touch_mellee(
            self,
            bullet_width: int,
            bullet_height: int,
            bullet_color: tuple[int, int, int],
            bullet_damage: int,
            state
    ) -> None:

        bullet = getattr(self, "_melee_bullet", None)

        # RECREATE if bullet does not exist OR was removed from global list
        if bullet is None or bullet not in state.enemy_bullets:
            bullet = Bullet(self.x, self.y)
            bullet.width = bullet_width
            bullet.height = bullet_height
            bullet.color = bullet_color
            bullet.damage = bullet_damage

            bullet.vx = 0
            bullet.vy = 0
            bullet.bullet_speed = 0

            bullet.update_rect()

            state.enemy_bullets.append(bullet)
            self._melee_bullet = bullet

        # ALWAYS follow enemy
        bullet.x = self.x + (self.width - bullet.width) // 2
        bullet.y = self.y + (self.height - bullet.height) // 2
        bullet.update_rect()
        # how to call
        # self.touch_mellee(
        #     bullet_width=40,
        #     bullet_height=40,
        #     bullet_color=GlobalConstants.RED,
        #     bullet_damage=11
        # )
    #
    # def Hunt_NPC(self, target_enemy) -> None:
    #     if target_enemy is None or self.camera is None:
    #         return
    #
    #     # direction toward target (world space)
    #     if target_enemy.x > self.x:
    #         self.mover.enemy_move_right(self)
    #     elif target_enemy.x < self.x:
    #         self.mover.enemy_move_left(self)
    #
    #     if target_enemy.y > self.y:
    #         self.mover.enemy_move_down(self)
    #     elif target_enemy.y < self.y:
    #         self.mover.enemy_move_up(self)
    #
    #     self.update_hitbox()
    def Hunt_NPC(self, target_enemy, state) -> None:
        if target_enemy is None or self.camera is None:
            return

        # move toward target (via MoveRectangle)
        if target_enemy.x > self.x:
            self.mover.enemy_move_right(self)
        elif target_enemy.x < self.x:
            self.mover.enemy_move_left(self)

        if target_enemy.y > self.y:
            self.mover.enemy_move_down(self)
        elif target_enemy.y < self.y:
            self.mover.enemy_move_up(self)

        self.update_hitbox()

        # collision → erase NPC
        if self.hitbox.colliderect(target_enemy.hitbox):
            if target_enemy in state.enemies:
                state.enemies.remove(target_enemy)

    def pounce(self) -> None:
        if self.target_player is None or self.camera is None:
            return

        now = pygame.time.get_ticks()

        # ---------------------------------
        # INIT STATE (once, no __init__ use)
        # ---------------------------------
        if not hasattr(self, "_pounce_active"):
            self._pounce_active = False          # slow mode default
            self._pounce_start_time = 0
            self._pounce_cooldown_until = 0

        # ---------------------------------
        # VECTOR TO PLAYER
        # ---------------------------------
        dx = self.target_player.x - self.x
        dy = self.target_player.y - self.y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist == 0:
            return

        # ---------------------------------
        # STATE TRANSITIONS
        # ---------------------------------
        # ENTER POUNCE
        if (
            not self._pounce_active
            and dist <= 100
            and now >= self._pounce_cooldown_until
        ):
            self._pounce_active = True
            self._pounce_start_time = now

        # EXIT POUNCE AFTER 3s
        if self._pounce_active and now - self._pounce_start_time >= 1000:
            self._pounce_active = False
            self._pounce_cooldown_until = now + 5000  # 5s cooldown

        # ---------------------------------
        # SPEED BY STATE
        # ---------------------------------
        speed = self.moveSpeed
        if self._pounce_active:
            speed = self.moveSpeed * 4

        # ---------------------------------
        # MOVE
        # ---------------------------------
        self.x += (dx / dist) * speed
        self.y += (dy / dist) * speed
        self.update_hitbox()

        # ---------------------------------
        # DAMAGE ON CONTACT
        # ---------------------------------
        if self.hitbox.colliderect(self.target_player.hitbox):
            if hasattr(self.target_player, "take_damage"):
                self.target_player.take_damage(self.bullet_damage)

    def melee_strike(
            self,
            dash_speed: float,
            dash_duration_ms: int,
            melee_width: int,
            melee_height: int,
            melee_color: tuple[int, int, int],
            damage: int,
            cooldown_ms: int,
            state
    ) -> None:
        if self.target_player is None or self.camera is None:
            return

        now = pygame.time.get_ticks()

        # lazy init (NO __init__ edits)
        if not hasattr(self, "_melee_active"):
            self._melee_active = False
            self._melee_start_time = 0
            self._melee_last_end = 0
            self._melee_dx = 0.0
            self._melee_dy = 0.0
            self._melee_bullet = None

        # cooldown gate (only when idle)
        if not self._melee_active and now - self._melee_last_end < cooldown_ms:
            return

        # -------------------------
        # START MELEE
        # -------------------------
        if not self._melee_active:
            dx = self.target_player.x - self.x
            dy = self.target_player.y - self.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                return

            self._melee_dx = dx / dist
            self._melee_dy = dy / dist

            self._melee_active = True
            self._melee_start_time = now

        # -------------------------
        # END MELEE
        # -------------------------
        if now - self._melee_start_time >= dash_duration_ms:
            self._melee_active = False
            self._melee_last_end = now

            if self._melee_bullet and self._melee_bullet in state.enemy_bullets:
                state.enemy_bullets.remove(self._melee_bullet)
            self._melee_bullet = None
            return

        # -------------------------
        # DASH MOVEMENT (LIKE POUNCE)
        # -------------------------
        self.x += self._melee_dx * dash_speed
        self.y += self._melee_dy * dash_speed
        self.update_hitbox()

        # -------------------------
        # CREATE / UPDATE MELEE BULLET (RECT)
        # -------------------------
        bullet = self._melee_bullet

        if bullet is None or bullet not in state.enemy_bullets:
            bullet = Bullet(self.x, self.y)
            bullet.width = melee_width
            bullet.height = melee_height
            bullet.color = melee_color
            bullet.damage = damage

            bullet.vx = 0
            bullet.vy = 0
            bullet.bullet_speed = 0

            bullet.update_rect()
            state.enemy_bullets.append(bullet)
            self._melee_bullet = bullet





        bullet.update_rect()

        # position bullet IN FRONT of enemy
        bullet.x = (
                self.hitbox.centerx
                + self._melee_dx * (melee_width // 2)
                - melee_width // 2
        )

        bullet.y = (
                self.hitbox.centery
                + self._melee_dy * (melee_height // 2)
                - melee_height // 2
        )

        bullet.update_rect()

        bullet.update_rect()
        # how to call
        # self.melee_strike(
        #     dash_speed=1.0,
        #     dash_duration_ms=400,
        #     melee_width=22,
        #     melee_height=22,
        #     melee_color=(255, 0, 0),
        #     damage=15,
        #     cooldown_ms=5000,
        #     state=state
        # )

    def shoot_bullets_left_right(
            self,
            bullet_speed: float,
            bullet_width: int,
            bullet_height: int,
            bullet_color: tuple[int, int, int],
            bullet_damage: int,
            cooldown_ms: int,
            state
    ) -> None:
        if self.camera is None:
            return

        now = pygame.time.get_ticks()

        # lazy cooldown tracking (no __init__ changes)
        if not hasattr(self, "_shoot_lr_last_time"):
            self._shoot_lr_last_time = 0

        if now - self._shoot_lr_last_time < cooldown_ms:
            return

        self._shoot_lr_last_time = now

        center_y = self.y + self.height // 2 - bullet_height // 2

        # LEFT bullet
        bullet_left = Bullet(self.x, center_y)
        bullet_left.width = bullet_width
        bullet_left.height = bullet_height
        bullet_left.color = bullet_color
        bullet_left.damage = bullet_damage
        bullet_left.vx = -1
        bullet_left.vy = 0
        bullet_left.bullet_speed = bullet_speed
        bullet_left.update_rect()
        state.enemy_bullets.append(bullet_left)

        # RIGHT bullet
        bullet_right = Bullet(self.x + self.width, center_y)
        bullet_right.width = bullet_width
        bullet_right.height = bullet_height
        bullet_right.color = bullet_color
        bullet_right.damage = bullet_damage
        bullet_right.vx = 1
        bullet_right.vy = 0
        bullet_right.bullet_speed = bullet_speed
        bullet_right.update_rect()
        state.enemy_bullets.append(bullet_right)

    def shoot_bullets_up_down(
            self,
            bullet_speed: float,
            bullet_width: int,
            bullet_height: int,
            bullet_color: tuple[int, int, int],
            bullet_damage: int,
            cooldown_ms: int,
            state
    ) -> None:
        if self.camera is None:
            return

        now = pygame.time.get_ticks()

        # lazy cooldown tracking
        if not hasattr(self, "_shoot_ud_last_time"):
            self._shoot_ud_last_time = 0

        if now - self._shoot_ud_last_time < cooldown_ms:
            return

        self._shoot_ud_last_time = now

        center_x = self.x + self.width // 2 - bullet_width // 2

        # UP bullet
        bullet_up = Bullet(center_x, self.y)
        bullet_up.width = bullet_width
        bullet_up.height = bullet_height
        bullet_up.color = bullet_color
        bullet_up.damage = bullet_damage
        bullet_up.vx = 0
        bullet_up.vy = -1
        bullet_up.bullet_speed = bullet_speed
        bullet_up.update_rect()
        state.enemy_bullets.append(bullet_up)

        # DOWN bullet
        bullet_down = Bullet(center_x, self.y + self.height)
        bullet_down.width = bullet_width
        bullet_down.height = bullet_height
        bullet_down.color = bullet_color
        bullet_down.damage = bullet_damage
        bullet_down.vx = 0
        bullet_down.vy = 1
        bullet_down.bullet_speed = bullet_speed
        bullet_down.update_rect()
        state.enemy_bullets.append(bullet_down)
