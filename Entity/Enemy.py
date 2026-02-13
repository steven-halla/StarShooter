import math
import random
import pygame
from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet




class Enemy:
    def __init__(self):
        # size
        self.width: int = 0
        self.touch_damage: int = 0
        self.height: int = 0
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20
        # generic bullet config (base enemy default)
        self.bullet_speed: float = 0.0
        self.bullet_damage: int = 10
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

    def player_collide_damage(self, player) -> None:
        if not self.is_active:
            return

        if self.hitbox.colliderect(player.hitbox):

            if player.invincible:
                return

            damage = self.touch_damage
            old_health = player.shipHealth

            # Shield system handles shield → hull logic internally
            player.shield_system.take_damage(damage)
            player.on_hit()

            # Only trigger spark if hull was actually damaged
            if player.shipHealth < old_health:
                player.on_hit()

    # --------------------------------------------------
    # DAMAGE
    # --------------------------------------------------
    def take_damage(self, state, amount: int) -> None:

        # inside Enemy.update(), where bullet collision damage happens
        for bullet in state.player_bullets:
            if bullet.hitbox.colliderect(self.hitbox):

                # 🚫 ShootingUpBlock ignores damage
                if self.name == "ShootingUpBlock":
                    continue  # collision allowed, no damage

                self.take_damage(bullet.damage)
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
        bullet.owner = self.name if hasattr(self, "name") else self.__class__.__name__

        bullet.update_rect()
        state.enemy_bullets.append(bullet)

        #how to call for single shot
        # self.shoot_single_down_vertical_y(
        #     bullet_speed=4.0,
        #     bullet_width=20,
        #     bullet_height=20,
        #     bullet_color=self.bulletColor,
        #     bullet_damage=10,
        #     state = state
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
            #     bullet_spread=44,
            #     state = state
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

    def splatter_cannon(
            self,
            bullet_speed: float,
            bullet_width: int,
            bullet_height: int,
            bullet_color: tuple[int, int, int],
            bullet_damage: int,
            low_rand_range: float,
            high_rand_range: float,
            bullet_count: int,
            state
    ) -> None:
        if self.target_player is None:
            return

        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        px = self.target_player.hitbox.centerx
        py = self.target_player.hitbox.centery

        dx = px - cx
        dy = py - cy
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        base_vx = dx / dist
        base_vy = dy / dist

        for _ in range(bullet_count):
            b = Bullet(cx, cy)
            b.width = bullet_width
            b.height = bullet_height
            b.color = bullet_color
            b.damage = bullet_damage

            # Add randomness to the base aimed vector
            b.vx = base_vx + random.uniform(low_rand_range, high_rand_range)
            b.vy = base_vy + random.uniform(low_rand_range, high_rand_range)
            b.bullet_speed = bullet_speed

            b.update_rect()
            state.enemy_bullets.append(b)

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
    def shoot_napalm(
            self,
            bullet_speed: float,
            bullet_width: int,
            bullet_height: int,
            bullet_color: tuple[int, int, int],
            bullet_damage: int,
            travel_time: float,
            explosion_time: float,
            aoe_size: tuple[int, int],
            state
    ) -> None:
        if self.target_player is None:
            return

        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        # Target player position
        tx = self.target_player.x + self.target_player.width // 2
        ty = self.target_player.y + self.target_player.height // 2

        dx = tx - cx
        dy = ty - cy
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        vx = dx / dist
        vy = dy / dist

        napalm = EnemyNapalmBullet(
            cx, cy,
            travel_time=travel_time,
            explosion_time=explosion_time,
            aoe_size=aoe_size,
            color=bullet_color,
            damage=bullet_damage
        )
        napalm.width = bullet_width
        napalm.height = bullet_height
        napalm.vx = vx
        napalm.vy = vy
        napalm.bullet_speed = bullet_speed
        napalm.camera = self.camera

        napalm.update_rect()
        state.enemy_bullets.append(napalm)

        # how to call:
        # self.shoot_napalm(
        #     bullet_speed=4.0,
        #     bullet_width=15,
        #     bullet_height=15,
        #     bullet_color=(255, 100, 0),
        #     bullet_damage=20,
        #     travel_time=0.5,
        #     explosion_time=3.0,
        #     aoe_size=(60, 60),
        #     state=state
        # )

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

    def shoot_bullets_diag_ul_lr(
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

        if not hasattr(self, "_shoot_ul_lr_last_time"):
            self._shoot_ul_lr_last_time = 0

        if now - self._shoot_ul_lr_last_time < cooldown_ms:
            return

        self._shoot_ul_lr_last_time = now

        cx = self.x + self.width // 2 - bullet_width // 2
        cy = self.y + self.height // 2 - bullet_height // 2

        # UP-LEFT
        b1 = Bullet(cx, cy)
        b1.width = bullet_width
        b1.height = bullet_height
        b1.color = bullet_color
        b1.damage = bullet_damage
        b1.vx = -1
        b1.vy = -1
        b1.bullet_speed = bullet_speed
        b1.update_rect()
        state.enemy_bullets.append(b1)

        # DOWN-RIGHT
        b2 = Bullet(cx, cy)
        b2.width = bullet_width
        b2.height = bullet_height
        b2.color = bullet_color
        b2.damage = bullet_damage
        b2.vx = 1
        b2.vy = 1
        b2.bullet_speed = bullet_speed
        b2.update_rect()
        state.enemy_bullets.append(b2)
        # fun call
        # self.shoot_bullets_diag_ul_lr(
        #     bullet_speed=4.0,
        #     bullet_width=14,
        #     bullet_height=14,
        #     bullet_color=GlobalConstants.RED,
        #     bullet_damage=12,
        #     cooldown_ms=1500,
        #     state=state
        # )

    def shoot_bullets_diag_ur_ll(
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

        if not hasattr(self, "_shoot_ur_ll_last_time"):
            self._shoot_ur_ll_last_time = 0

        if now - self._shoot_ur_ll_last_time < cooldown_ms:
            return

        self._shoot_ur_ll_last_time = now

        cx = self.x + self.width // 2 - bullet_width // 2
        cy = self.y + self.height // 2 - bullet_height // 2

        # UP-RIGHT
        b1 = Bullet(cx, cy)
        b1.width = bullet_width
        b1.height = bullet_height
        b1.color = bullet_color
        b1.damage = bullet_damage
        b1.vx = 1
        b1.vy = -1
        b1.bullet_speed = bullet_speed
        b1.update_rect()
        state.enemy_bullets.append(b1)

        # DOWN-LEFT
        b2 = Bullet(cx, cy)
        b2.width = bullet_width
        b2.height = bullet_height
        b2.color = bullet_color
        b2.damage = bullet_damage
        b2.vx = -1
        b2.vy = 1
        b2.bullet_speed = bullet_speed
        b2.update_rect()
        state.enemy_bullets.append(b2)
        # fun call
        # self.shoot_bullets_diag_ur_ll(
        #     bullet_speed=4.0,
        #     bullet_width=14,
        #     bullet_height=14,
        #     bullet_color=GlobalConstants.RED,
        #     bullet_damage=12,
        #     cooldown_ms=1500,
        #     state=state
        # )

    def lay_bomb(
            self,
            width: int = 20,
            height: int = 20,
            explosion_timer_ms: int = 3000,  # 3 seconds explosion duration
            explosion_radius: int = 100,  # Larger explosion radius
            damage: int = 40,
            distance: float = 200,
            speed: float = 4.0,
            state=None,
            bullet=None,
            surface=None,
            camera=None
    ):


        now = pygame.time.get_ticks()

        # =========================
        # SPAWN MODE (create bullet)
        # =========================
        if state and bullet is None and surface is None and camera is None:
            if self.camera is None:
                return

            bullet = Bullet(self.x, self.y)
            bullet.width = width
            bullet.height = height
            bullet.color = (128, 0, 128)  # Purple color for egg
            bullet.damage = damage

            # center on enemy
            bullet.x = self.hitbox.centerx - width // 2
            bullet.y = self.hitbox.centery - height // 2

            # movement direction (toward player if thrown)
            if distance > 0 and self.target_player:
                dx = self.target_player.x - self.x
                dy = self.target_player.y - self.y
                dist = math.hypot(dx, dy)
                bullet.vx = dx / dist if dist != 0 else 0
                bullet.vy = dy / dist if dist != 0 else 0
            else:
                bullet.vx = 0
                bullet.vy = 0

            bullet.bullet_speed = speed

            # Internal bullet state
            bullet.spawn_time = now
            bullet.explode_time = now + explosion_timer_ms
            bullet.max_distance = distance
            bullet.traveled = 0
            bullet.exploded = False
            bullet.explosion_radius = explosion_radius
            bullet.explode_end = 0

            bullet.update_rect()
            state.enemy_bullets.append(bullet)
            return  # Spawn complete




    # ==================================================
    # the below should only stay as a temp example
    def create_bomb(self, width: int, height: int) -> None:
        # world-space rect (PERSISTENT: stored, not drawn here)
        x = int(self.x + (self.width - width) // 2)
        y = int(self.y + (self.height - height) // 2)

        self.bomb_rect = pygame.Rect(x, y, width, height)

        # KEEP PRINT
        print(f"bomb rect at x={x}, y={y}, w={width}, h={height}")

    def draw_bomb(self, surface: pygame.Surface, camera) -> None:
        if not hasattr(self, "bomb_rect"):
            return
        print("adfj;safljdsl;fsajf;a")

        sx = int(camera.world_to_screen_x(self.bomb_rect.x))
        sy = int(camera.world_to_screen_y(self.bomb_rect.y))
        sw = int(self.bomb_rect.width * camera.zoom)
        sh = int(self.bomb_rect.height * camera.zoom)

        pygame.draw.rect(surface, GlobalConstants.RED, (sx, sy, sw, sh))

    def moving_blades(
            self,
            monster_x: float,
            monster_y: float,
            monster_width: int,
            monster_height: int,
            blade_width: int,
            blade_height: int,
            blade_color: tuple[int, int, int],
            damage: int,
            x_offset: int,
            y_offset: int,
            state
    ) -> None:
        if state is None:
            return

        # lazy init (NO __init__ changes)
        if not hasattr(self, "_blade"):
            self._blade = None
            self._blade_params = None

        blade = self._blade

        # CREATE blade if missing
        if blade is None or blade not in state.enemy_bullets:
            blade = Bullet(0, 0)
            blade.width = blade_width
            blade.height = blade_height
            blade.color = blade_color
            blade.damage = damage
            blade.vx = 0
            blade.vy = 0
            blade.bullet_speed = 0
            blade.update_rect()

            # Store the parameters for future updates
            self._blade_params = {
                "width": blade_width,
                "height": blade_height,
                "x_offset": x_offset,
                "y_offset": y_offset
            }

            state.enemy_bullets.append(blade)
            self._blade = blade

        # Use the current enemy position instead of the passed-in position
        if self._blade_params:
            blade.x = (
                    self.x
                    + self.width // 2
                    - self._blade_params["width"] // 2
                    + self._blade_params["x_offset"]
            )

            blade.y = (
                    self.y
                    + self.height // 2
                    - self._blade_params["height"] // 2
                    + self._blade_params["y_offset"]
            )

            # Print enemy and blade positions for debugging
            print(f"Enemy position: x={self.x:.2f}, y={self.y:.2f}")
            print(f"Blade position: x={blade.x:.2f}, y={blade.y:.2f}")

        blade.update_rect()
        # how to call
        # self.moving_blades(
        #     monster_x=self.x,
        #     monster_y=self.y,
        #     monster_width=self.width,
        #     monster_height=self.height,
        #     blade_width=10,
        #     blade_height=36,
        #     blade_color=(0, 255, 0),
        #     damage=25,
        #     x_offset=0,
        #     y_offset=-28,
        #     state=state
        # )


    # need to update this with params for brea
    def dragons_breath(
            self,
            monster_x: float,
            monster_y: float,
            monster_width: int,
            monster_height: int,
            length: int,
            min_width: int,
            max_width: int,
            segments: int,
            color: tuple[int, int, int],
            damage: int,
            x_offset: int,
            y_offset: int,
            state
    ) -> None:
        if state is None:
            return



        # lazy init (NO __init__ changes)
        if not hasattr(self, "_dragon_cone"):
            self._dragon_cone = []

        cone = self._dragon_cone

        # ensure correct number of segments
        while len(cone) < segments:
            b = Bullet(0, 0)
            b.remove_type = 1

            b.vx = 0
            b.vy = 0
            b.bullet_speed = 0
            b.color = color
            b.damage = damage
            cone.append(b)
            state.enemy_bullets.append(b)

        while len(cone) > segments:
            b = cone.pop()
            if b in state.enemy_bullets:
                state.enemy_bullets.remove(b)

        # cone geometry
        segment_length = length / segments

        for i, bullet in enumerate(cone):
            t = i / (segments - 1) if segments > 1 else 0

            # interpolate width (narrow → wide)
            width = int(min_width + (max_width - min_width) * t)
            height = int(segment_length)

            bullet.width = width
            bullet.height = height

            # base center of enemy
            base_x = monster_x + monster_width // 2 + x_offset
            base_y = monster_y + monster_height + y_offset

            # position downward cone
            bullet.x = base_x - width // 2
            bullet.y = base_y + i * segment_length

            bullet.update_rect()
            # how to call
            # self.dragons_breath(
            #     monster_x=self.x,
            #     monster_y=self.y,
            #     monster_width=self.width,
            #     monster_height=self.height,
            #     length=120,
            #     min_width=10,
            #     max_width=60,
            #     segments=6,
            #     color=(255, 120, 0),
            #     damage=18,
            #     x_offset=0,
            #     y_offset=0,
            #     state=state
            # )

    def rope_grab(
            self,
            rope_length: int,
            rope_width: int,
            rope_speed: float,
            rope_duration_ms: int,  # ✅ PASSED IN
            rope_color: tuple[int, int, int],
            state
    ) -> None:
        if self.target_player is None or self.camera is None:
            return

        now = pygame.time.get_ticks()

        # lazy init (NO __init__ edits)
        if not hasattr(self, "_rope"):
            self._rope = None

        rope = self._rope

        # ---------------------------------
        # CREATE rope bullet if missing
        # ---------------------------------
        if rope is None or rope not in state.enemy_bullets:
            rope = Bullet(0, 0)
            rope.width = rope_width
            rope.height = rope_width
            rope.color = rope_color
            rope.damage = 0

            rope.start = pygame.Vector2(0, 0)
            rope.end = pygame.Vector2(0, 0)

            rope.current_length = 0.0
            rope.end_time = now + rope_duration_ms  # ✅ USE PARAM
            rope.extend_lock = False

            rope.vx = 0
            rope.vy = 0
            rope.bullet_speed = 0

            rope.update_rect()
            state.enemy_bullets.append(rope)
            self._rope = rope

        # ---------------------------------
        # DESPAWN AFTER TIME
        # ---------------------------------
        if now >= rope.end_time:
            if rope in state.enemy_bullets:
                state.enemy_bullets.remove(rope)
            self._rope = None
            self.player_caught = False
            return

        # ---------------------------------
        # AIM AT PLAYER
        # ---------------------------------
        bx = self.x + self.width / 2
        by = self.y + self.height / 2

        px = self.target_player.x + self.target_player.width / 2
        py = self.target_player.y + self.target_player.height / 2

        dx = px - bx
        dy = py - by
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        dx /= dist
        dy /= dist

        # ---------------------------------
        # EXTEND ROPE
        # ---------------------------------
        rope.current_length = min(
            rope_length,
            rope.current_length + rope_speed
        )

        end_x = bx + dx * rope.current_length
        end_y = by + dy * rope.current_length

        rope.start.x = bx
        rope.start.y = by
        rope.end.x = end_x
        rope.end.y = end_y

        # ---------------------------------
        # LOGIC RECT (midpoint)
        # ---------------------------------
        mid_x = (bx + end_x) / 2
        mid_y = (by + end_y) / 2

        rope.x = mid_x - rope.width // 2
        rope.y = mid_y - rope.height // 2
        rope.update_rect()

        # ---------------------------------
        # COLLISION → EXTEND DURATION
        # ---------------------------------
        thickness = rope.width
        rope_rect = pygame.Rect(
            min(rope.start.x, rope.end.x) - thickness,
            min(rope.start.y, rope.end.y) - thickness,
            abs(rope.end.x - rope.start.x) + thickness * 2,
            abs(rope.end.y - rope.start.y) + thickness * 2
        )

        if rope_rect.colliderect(self.target_player.melee_hitbox):
            self.player_caught = True
            if not rope.extend_lock:
                rope.end_time = now + rope_duration_ms  # SET to 3 seconds from NOW, don't ADD
                rope.extend_lock = True
        else:
            # DON'T reset extend_lock here - keep it locked once caught
            if not self.player_caught:
                rope.extend_lock = False
            self.player_caught = False
        #
        # self.rope_grab(
        #     rope_length=160,
        #     rope_width=4,
        #     rope_speed=3.0,
        #     rope_duration_ms=3000,
        #     rope_color=(180, 180, 180),
        #     state=state
        # )

    def draw_rope(self, surface: pygame.Surface, camera) -> None:
        if not hasattr(self, "_rope") or self._rope is None:
            return

        rope = self._rope

        # 🔑 KILL VISUAL RECT (logic rect still exists elsewhere)
        rope.width = 0
        rope.height = 0
        rope.rect.width = 0
        rope.rect.height = 0

        pygame.draw.line(
            surface,
            rope.color,
            (
                camera.world_to_screen_x(rope.start.x),
                camera.world_to_screen_y(rope.start.y),
            ),
            (
                camera.world_to_screen_x(rope.end.x),
                camera.world_to_screen_y(rope.end.y),
            ),
            max(1, int(rope.original_width * camera.zoom))
            if hasattr(rope, "original_width")
            else max(1, int(4 * camera.zoom)),
        )

    # how to call (update)
    # self.rope_grab(
    #     rope_length=160,
    #     rope_width=6,
    #     rope_color=(180, 180, 180),
    #     state=state
    # )

    # how to call (draw)
    # self.draw_rope(surface, camera)
    # def check_rope_collision(self, player) -> bool:
    #     """Check if rope bullet collides with player and print message"""
    #     if not hasattr(self, "_rope") or self._rope is None:
    #         return False
    #
    #     rope_rect = pygame.Rect(
    #         self._rope.x,
    #         self._rope.y,
    #         self._rope.width,
    #         self._rope.height
    #     )
    #
    #     if rope_rect.colliderect(player.hitbox):
    #         print("🔴 ROPE HIT PLAYER!")
    #         return True
    #
    #     return False
    def check_rope_collision(self, player) -> None:
        if player is None or self._rope is None or self.camera is None:
            return

        rope = self._rope

        thickness = rope.width

        x1, y1 = rope.start.x, rope.start.y
        x2, y2 = rope.end.x, rope.end.y

        rope_rect = pygame.Rect(
            min(x1, x2) - thickness,
            min(y1, y2) - thickness,
            abs(x2 - x1) + thickness * 2,
            abs(y2 - y1) + thickness * 2
        )

        if rope_rect.colliderect(player.hitbox):
            print("ROPE SLAM ACTIVE")

            # 🔒 FORCE player to top-left EVERY FRAME
            player.x = self.camera.x
            player.y = self.camera.y

            # keep hitbox in sync
            player.update_hitbox()


class EnemyNapalmBullet(Bullet):
    def __init__(self, x: float, y: float, travel_time: float, explosion_time: float, aoe_size: tuple[int, int],
                 color: tuple[int, int, int], damage: int):
        super().__init__(x, y)
        self.color = color
        self.damage = damage

        # Phases logic similar to NapalmSpread
        self.travel_timer = Timer(travel_time)
        self.travel_timer.reset()

        self.explosion_timer = Timer(explosion_time)
        self.has_exploded = False

        self.aoe_width, self.aoe_height = aoe_size
        self.aoe_rect = pygame.Rect(0, 0, 0, 0)

    def update(self) -> None:
        if not self.has_exploded:
            if not self.travel_timer.is_ready():
                super().update()
            else:
                self.trigger_explosion()
        else:
            if self.explosion_timer.is_ready():
                self.is_active = False

    def trigger_explosion(self) -> None:
        if self.has_exploded:
            return
        self.has_exploded = True
        self.vx = 0.0
        self.vy = 0.0
        self.explosion_timer.reset()

        # Center AOE on current position
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        self.aoe_rect = pygame.Rect(
            cx - self.aoe_width // 2,
            cy - self.aoe_height // 2,
            self.aoe_width,
            self.aoe_height
        )
        # Update main rect to AOE rect for collision detection in game loop
        self.rect = self.aoe_rect

    def collide_with_rect(self, other: pygame.Rect) -> bool:
        if self.rect.colliderect(other):
            if not self.has_exploded:
                self.trigger_explosion()
                return True  # Direct hit triggers explosion
            return True  # In AOE
        return False

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.is_active:
            return

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        if not self.has_exploded:
            pygame.draw.rect(
                surface,
                self.color,
                pygame.Rect(
                    screen_x,
                    screen_y,
                    int(self.width * camera.zoom),
                    int(self.height * camera.zoom),
                ),
            )
        else:
            # Draw AOE
            aoe_screen_x = camera.world_to_screen_x(self.aoe_rect.x)
            aoe_screen_y = camera.world_to_screen_y(self.aoe_rect.y)
            pygame.draw.rect(
                surface,
                self.color,
                pygame.Rect(
                    aoe_screen_x,
                    aoe_screen_y,
                    int(self.aoe_width * camera.zoom),
                    int(self.aoe_height * camera.zoom),
                ),
                2  # Outline for AOE
            )

#####
# new mellee : Grabber, grabs player so they have to shoot to get out.
# new melle: hook shot, grab player and put them in new position
