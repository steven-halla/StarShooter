import pygame
import pytmx
import math
from Constants.GlobalConstants import GlobalConstants
from Controller.KeyBoardControls import KeyBoardControls
from Entity.Enemy import Enemy
from Entity.Monsters.Coins import Coins
from Entity.StarShip import StarShip
from Movement.MoveRectangle import MoveRectangle
from SaveStates.SaveState import SaveState
from ScreenClasses.Camera import Camera
from ScreenClasses.TextBox import TextBox

class VerticalBattleScreen:
    def __init__(self, textbox):
        self.starship = StarShip()
        self.playerDead: bool = False
        self.textbox = textbox
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
        self.WORLD_HEIGHT: int = GlobalConstants.GAMEPLAY_HEIGHT * 3
        self.SCROLL_SPEED_PER_SECOND: float = 55.0
        self.camera_y: float = 0.0
        self.SCROLL_SPEED_PER_FRAME: float = 55.0
        window_width: int = GlobalConstants.BASE_WINDOW_WIDTH
        window_height: int = GlobalConstants.GAMEPLAY_HEIGHT
        self.window_width = window_width
        self.window_height = window_height
        self.camera = Camera(
            window_width=window_width,
            window_height=window_height,
            world_height=self.WORLD_HEIGHT,
            scroll_speed_per_frame=self.SCROLL_SPEED_PER_FRAME,
            initial_zoom=2.5,   # DO NOT TOUCH CAMERA SETTINGS
        )
        self.save_state = SaveState()

        self.hud_sheet = pygame.image.load(
            "./Assets/Images/hud_icons.png"
        ).convert_alpha()

        self.hud_sheet = pygame.image.load(
            "./Assets/Images/hud_icons.png"
        ).convert_alpha()

        ICON_SIZE = 16
        UI_ICON_SIZE = 24

        ICON_MAP = {
            0: "heart_icon",
            1: "buster_cannon_icon",
            2: "wind_slicer_icon",
            3: "napalm_spread_icon",
            4: "energy_ball_icon",
            5: "plasma_blaster_icon",
            6: "metal_shield_icon",
            8: "beam_saber_icon",
            9: "wave_crash_icon",
            10: "engine_icon",
        }

        for index, attr_name in ICON_MAP.items():
            rect = pygame.Rect(index * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
            icon = self.hud_sheet.subsurface(rect)
            setattr(
                self,
                attr_name,
                pygame.transform.scale(icon, (UI_ICON_SIZE, UI_ICON_SIZE))
            )

        self.missile_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(pygame.Rect(7 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)),
            (32, 32)
        )

        self.SUB_WEAPON_ICON_INDEX = {
            "Buster Cannon": 1,
            "Wind Slicer": 2,
            "Napalm Spread": 3,
            "Energy Ball": 4,
            "Plasma Blaster": 5,
            "Metal Shield": 6,
            "Beam Saber": 8,
            "Wave Crash": 9,
        }

        self.sub_weapon_icons = {}

        self.textbox = TextBox(
            GlobalConstants.BASE_WINDOW_WIDTH,
            GlobalConstants.BASE_WINDOW_HEIGHT
        )
        self.textbox.show("")
    def start(self, state):
        pass

    def set_player(self, player):
        self.starship = player


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
        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = GlobalConstants.GAMEPLAY_HEIGHT

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

    def update(self, state: 'GameState'):

        self.controller.update()

        # THEN: react to input
        if self.textbox.is_visible():
            if self.controller.qJustPressed:
                self.textbox.advance()

        self.move_map_y_axis()
        self.controller.update()

        self.move_player_x_y()
        self.starship.update()
        self.clamp_starship_to_screen()
        self.fire_all_weapons(state)
        self.weapon_helper(state)
        self.bullet_helper(state)
        self.metal_shield_helper()

        # Collect enemy bullets - moved from draw method to update method
        for enemy in state.enemies:
            if hasattr(enemy, "enemyBullets"):
                for b in enemy.enemyBullets:
                    self.enemy_bullets.append(b)
                enemy.enemyBullets.clear()

        self.bullet_collision_helper_remover(state)
        self.collision_tile_helper(state)
        self.rect_helper(state)
        UI_KILL_PADDING = 12  # pixels ABOVE the UI panel (tweak this)

        screen_bottom = (
                self.camera.y
                + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)
                - UI_KILL_PADDING
        )

        for enemy in list(state.enemies):
            # ❌ skip coins
            if isinstance(enemy, Coins):
                continue

            # enemy is BELOW visible gameplay area
            if enemy.y > screen_bottom:
                enemy.is_active = False
                state.enemies.remove(enemy)

    def move_player_x_y(self):
        if not self.playerDead:
            if self.controller.left_button:
                self.mover.player_move_left(self.starship)
            if self.controller.right_button:
                self.mover.player_move_right(self.starship)
            if self.controller.up_button:
                self.mover.player_move_up(self.starship)
            if self.controller.down_button:
                self.mover.player_move_down(self.starship)

    def draw(self, state) -> None:
        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        scene_surface = pygame.Surface((window_width, window_height))
        # scene_surface.fill((0, 0, 0))  # OR sky color
        scene_surface.fill((20, 20, 40))  # sky / space color
        zoom = self.camera.zoom

        for weapon_name, icon_index in self.SUB_WEAPON_ICON_INDEX.items():
            rect = pygame.Rect(icon_index * 16, 0, 16, 16)
            icon = self.hud_sheet.subsurface(rect)
            self.sub_weapon_icons[weapon_name] = pygame.transform.scale(icon, (24, 24))

        self.draw_tiled_layers(scene_surface)

        if hasattr(self, "draw_level_collision"):
            self.draw_collision_tiles(scene_surface)

        # Scale gameplay scene
        scaled_scene = pygame.transform.scale(
            scene_surface,
            (int(window_width * zoom), int(window_height * zoom))
        )

        # Clear full display (includes UI area)
        state.DISPLAY.fill(GlobalConstants.BLACK)

        # Draw gameplay area at top
        state.DISPLAY.blit(scaled_scene, (0, 0))

        self.draw_sub_weapon_rect_helper(state)

        # 2️⃣ DRAW ENEMY BULLETS WITH CAMERA TRANSFORM - Draw before UI panel
        # print(f"[DRAW] Drawing {len(self.enemy_bullets)} enemy bullets")
        for bullet in self.enemy_bullets:
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * self.camera.zoom)
            bh = int(bullet.height * self.camera.zoom)

            # Debug print to show bullet screen coordinates
            # print(f"[DRAW BULLET] screen_pos=({bx:.1f},{by:.1f}), world_pos=({bullet.x:.1f},{bullet.y:.1f})")

            # Draw a larger, more visible bullet for debugging
            pygame.draw.rect(
                state.DISPLAY,
                (255, 0, 0),  # RED for better visibility
                pygame.Rect(bx-2, by-2, bw+4, bh+4),
                0
            )

            # Draw the actual bullet
            pygame.draw.rect(
                state.DISPLAY,
                (0, 255, 0),  # GREEN
                pygame.Rect(bx, by, bw, bh),
                0
            )

        # Draw explosion rects using lay_bomb
        for enemy in state.enemies:
            if hasattr(enemy, "lay_bomb"):
                for bullet in self.enemy_bullets:
                    enemy.lay_bomb(bullet=bullet, surface=state.DISPLAY, camera=self.camera)

        # 🔽 UI PANEL (BOTTOM BAR) - Draw last to ensure it covers anything that comes into contact with it
        self.draw_ui_panel(state.DISPLAY)

        # 3️⃣ (OPTIONAL DEBUG) CONFIRM ALIGNMENT
        # PLAYER HITBOX DRAW — SAME SPACE
        px = self.camera.world_to_screen_x(self.starship.hitbox.x)
        py = self.camera.world_to_screen_y(self.starship.hitbox.y)
        pw = int(self.starship.hitbox.width * self.camera.zoom)
        ph = int(self.starship.hitbox.height * self.camera.zoom)

        pygame.draw.rect(
            state.DISPLAY,
            (255, 0, 0),
            pygame.Rect(px, py, pw, ph),
            2
        )
        # for enemy in state.enemies:
        #     enemy.update()
        #
        #     if getattr(enemy, "has_barrage", False):
        #         # ONLY BossLevelSix has these methods
        #         enemy.draw_barrage(state.DISPLAY, self.camera)
        #         enemy.apply_barrage_damage(self.starship)

    def bullet_helper(self, state):
        for bullet in list(self.player_bullets):

            # -------------------------
            # METAL SHIELD (uses rect, not hitbox)
            # -------------------------
            if bullet.weapon_name == "Metal Shield":
                shield_rect = bullet.rect

                for enemy in list(state.enemies):
                    if shield_rect.colliderect(enemy.hitbox):
                        enemy.enemyHealth -= bullet.damage
                        if enemy.enemyHealth <= 0:
                            self.remove_enemy_if_dead(enemy, state)
                continue

            # -------------------------
            # ALL OTHER BULLETS
            # -------------------------
            if not hasattr(bullet, "rect"):
                continue

            bullet_rect = bullet.rect

            for enemy in list(state.enemies):
                # Skip coins - they should only be collected by starship collision
                if hasattr(enemy, "__class__") and enemy.__class__.__name__ == "Coins":
                    continue

                if not bullet_rect.colliderect(enemy.hitbox):
                    continue

                enemy.enemyHealth -= getattr(bullet, "damage", 0)

                if hasattr(bullet, "trigger_explosion"):
                    bullet.trigger_explosion()
                elif getattr(bullet, "is_piercing", False):
                    pass
                else:
                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)

                if enemy.enemyHealth <= 0:
                    self.remove_enemy_if_dead(enemy, state)
                break

    def remove_enemy_if_dead(self, enemy, state) -> None:
        if enemy.enemyHealth > 0:
            return

        enemy.is_active = False

        if enemy in state.enemies:
            state.enemies.remove(enemy)

    def get_enemy_screen_rect(self, enemy) -> pygame.Rect:
        return pygame.Rect(
            self.camera.world_to_screen_x(enemy.x),
            self.camera.world_to_screen_y(enemy.y),
            int(enemy.width * self.camera.zoom),
            int(enemy.height * self.camera.zoom)
        )

    def weapon_rectangle(self, obj) -> pygame.Rect:
        return pygame.Rect(
            self.camera.world_to_screen_x(obj.x),
            self.camera.world_to_screen_y(obj.y),
            int(obj.width * self.camera.zoom),
            int(obj.height * self.camera.zoom)
        )

    def draw_player_hp_bar(self, surface):
        """
        Draws player HP text at the top of the screen.
        Format: HP: current/100
        """
        font = pygame.font.Font(None, 24)
        current_hp = max(0, int(self.starship.shipHealth))
        max_hp = 100
        hp_text = f"HP: {current_hp}/{max_hp}"
        text_surface = font.render(hp_text, True, (255, 255, 255))
        # Top-left padding
        surface.blit(text_surface, (10, 10))

    def draw_ui_panel(self, surface: pygame.Surface) -> None:
        font = pygame.font.Font(None, 24)

        missile_text = f"{self.starship.missile.current_missiles}/{self.starship.missile.max_missiles}"
        missile_text_surface = font.render(missile_text, True, (255, 255, 255))
        # -----------------------------
        # PANEL RECT
        # -----------------------------
        panel_rect = pygame.Rect(
            0,
            GlobalConstants.GAMEPLAY_HEIGHT,
            GlobalConstants.BASE_WINDOW_WIDTH,
            GlobalConstants.UI_PANEL_HEIGHT
        )

        pygame.draw.rect(surface, (20, 20, 20), panel_rect)

        pygame.draw.line(
            surface,
            (255, 255, 255),
            (0, GlobalConstants.GAMEPLAY_HEIGHT),
            (GlobalConstants.BASE_WINDOW_WIDTH, GlobalConstants.GAMEPLAY_HEIGHT),
            2
        )

        # -----------------------------
        # Get current HP values
        # -----------------------------
        current_hp = max(0, int(self.starship.shipHealth))
        max_hp = max(1, int(self.starship.shipHealthMax))

        # -----------------------------
        # HP BAR
        # -----------------------------
        BAR_WIDTH = 100
        BAR_HEIGHT = 20

        hp_percent = current_hp / max_hp
        filled_width = max(0, min(BAR_WIDTH, int(BAR_WIDTH * hp_percent)))

        # Position the bar directly after the heart image
        bar_x = 50  # Starting position for the bar
        bar_y = GlobalConstants.GAMEPLAY_HEIGHT + 10

        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT),
            1
        )

        if filled_width > 0:
            pygame.draw.rect(
                surface,
                (0, 200, 0),
                (bar_x + 1, bar_y + 1, filled_width - 2, BAR_HEIGHT - 2)
            )

        # -----------------------------
        # HUD ICON (LOAD ONCE)
        # -----------------------------

        # -----------------------------
        # HEART ICON (PRELOADED, NO IMAGE.LOAD HERE)
        # -----------------------------

        # draw heart icon (already sliced + scaled in __init__)
        heart_x = 10
        heart_y = GlobalConstants.GAMEPLAY_HEIGHT + 6
        surface.blit(self.heart_icon, (heart_x, heart_y))

        # -----------------------------
        # HP BAR (POSITIONED AFTER HEART)
        # -----------------------------

        bar_x = heart_x + self.heart_icon.get_width() + 8
        bar_y = GlobalConstants.GAMEPLAY_HEIGHT + 10

        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT),
            1
        )

        if filled_width > 0:
            pygame.draw.rect(
                surface,
                (0, 200, 0),
                (bar_x + 1, bar_y + 1, filled_width - 2, BAR_HEIGHT - 2)
            )

        # -----------------------------
        # MISSILE ICON (PRELOADED)
        # -----------------------------

        icon_x = bar_x + BAR_WIDTH + 10
        icon_y = bar_y - 4
        surface.blit(self.missile_icon, (icon_x, icon_y))

        # -----------------------------
        # MISSILE COUNT TEXT
        # -----------------------------

        font = pygame.font.Font(None, 24)
        missile_text = f"{self.starship.missile.current_missiles}/{self.starship.missile.max_missiles}"
        missile_surface = font.render(missile_text, True, (255, 255, 255))

        missile_text_x = icon_x + 32 + 5
        missile_text_y = icon_y + 8

        surface.blit(missile_text_surface, (missile_text_x, missile_text_y))
        # -----------------------------
        # EQUIPPED WEAPON ICON POSITION
        # -----------------------------

        buster_icon_x = missile_text_x + missile_surface.get_width() + 16
        buster_icon_y = icon_y + 8

        # Draw yellow box for image placeholder (smaller size)
        box_x = missile_text_x + missile_surface.get_width() + 10
        box_y = icon_y + 4  # Align with the missile icon vertically, moved down by 4 pixels
        box_width = 40  # Width is good
        box_height = 36  # Reduced height further

        # Draw the number "1" in the middle of the top line of the box (bigger font)
        number_font = pygame.font.Font(None, 28)  # Increased from 20 to make the number bigger
        number_text = "1"
        number_surface = number_font.render(number_text, True, (255, 255, 0))  # Yellow text

        # Position the number in the middle of the top line
        number_x = box_x + (box_width - number_surface.get_width()) // 2
        number_y = box_y - number_surface.get_height() // 2  # Position number to be centered on the top line

        # Draw the yellow box with gaps in the top line for the number
        # Left side
        pygame.draw.line(
            surface,
            (255, 255, 0),  # Yellow color
            (box_x, box_y),
            (number_x - 5, box_y),  # Stop 5 pixels before the number (increased from 3 for larger font)
            1  # 1 pixel width for the line
        )

        # Right side
        pygame.draw.line(
            surface,
            (255, 255, 0),  # Yellow color
            (number_x + number_surface.get_width() + 5, box_y),  # Start 5 pixels after the number (increased from 3)
            (box_x + box_width, box_y),
            1  # 1 pixel width for the line
        )

        # Bottom line
        pygame.draw.line(
            surface,
            (255, 255, 0),  # Yellow color
            (box_x, box_y + box_height - 4),
            (box_x + box_width, box_y + box_height - 4),
            1  # 1 pixel width for the line
        )

        # Left side line
        pygame.draw.line(
            surface,
            (255, 255, 0),  # Yellow color
            (box_x, box_y),
            (box_x, box_y + box_height - 4),
            1  # 1 pixel width for the line
        )

        # Right side line
        pygame.draw.line(
            surface,
            (255, 255, 0),  # Yellow color
            (box_x + box_width, box_y),
            (box_x + box_width, box_y + box_height - 4),
            1  # 1 pixel width for the line
        )

        # Draw the number
        surface.blit(number_surface, (number_x, number_y))

    # FIX — use the variables that actually exist above

        # buster_icon_x = missile_text_x + missile_surface.get_width() + 16
        # buster_icon_y = icon_y  + 10
        #
        # surface.blit(self.buster_cannon_icon, (buster_icon_x, buster_icon_y))
        #
        weapon_name = self.starship.equipped_magic[0]

        if weapon_name is not None:
            icon_index = self.SUB_WEAPON_ICON_INDEX.get(weapon_name)

            if icon_index is not None:
                icon_rect = pygame.Rect(icon_index * 16, 0, 16, 16)
                icon = self.hud_sheet.subsurface(icon_rect)
                icon = pygame.transform.scale(icon, (24, 24))

                surface.blit(icon, (buster_icon_x, buster_icon_y))

    def draw_tiled_layers(self, surface: pygame.Surface) -> None:
        tile_size = self.tile_size
        window_height = GlobalConstants.GAMEPLAY_HEIGHT

        # Ordered render: BACKGROUND → GROUND → HAZARD
        for layer_name in ("background", "hazard"):
            layer = self.tiled_map.get_layer_by_name(layer_name)

            for col, row, image in layer.tiles():
                if image is None:
                    continue

                world_y = row * tile_size
                screen_y = world_y - self.camera_y

                # Cull off-screen tiles
                if screen_y + tile_size < 0 or screen_y > window_height:
                    continue

                surface.blit(image, (col * tile_size, screen_y))

    def update_collision_tiles(self, state, damage: int = 5) -> None:
        layer = self.tiled_map.get_layer_by_name("collision")
        tile_size = self.tile_size
        KNOCKBACK = 4

        # ---------- PLAYER (PURE VECTOR vx / vy) ----------
        player = self.starship
        player_rect = player.hitbox

        player_center_x = player_rect.centerx
        player_center_y = player_rect.centery

        for col, row, image in layer.tiles():
            if image is None:
                continue

            tile_rect = pygame.Rect(
                col * tile_size,
                row * tile_size,
                tile_size,
                tile_size
            )

            if player_rect.colliderect(tile_rect):
                if not player.invincible:
                    player.shipHealth -= damage
                    player.on_hit()

                tile_center_x = tile_rect.centerx
                tile_center_y = tile_rect.centery

                # vector from tile → player
                vx = player_center_x - tile_center_x
                vy = player_center_y - tile_center_y

                length = math.hypot(vx, vy)
                if length != 0:
                    vx /= length
                    vy /= length

                # apply knockback via vector velocity only
                player.vx = vx * KNOCKBACK
                player.vy = vy * KNOCKBACK

                # prevent player from entering collision tiles by adjusting position
                # calculate the minimum distance needed to move the player out of the tile
                overlap_x = (player_rect.width + tile_rect.width) / 2 - abs(player_center_x - tile_center_x)
                overlap_y = (player_rect.height + tile_rect.height) / 2 - abs(player_center_y - tile_center_y)

                # move the player in the direction of least resistance
                if overlap_x < overlap_y:
                    if player_center_x < tile_center_x:
                        player.x -= overlap_x
                    else:
                        player.x += overlap_x
                else:
                    if player_center_y < tile_center_y:
                        player.y -= overlap_y
                    else:
                        player.y += overlap_y

                # update the hitbox to reflect the new position
                player.update_hitbox()

                break

        # ---------- ENEMIES (PURE VECTOR vx / vy, WITH PENETRATION PREVENTION) ----------
        for enemy in list(state.enemies):
            enemy_rect = enemy.hitbox
            enemy_cx = enemy_rect.centerx
            enemy_cy = enemy_rect.centery

            for col, row, image in layer.tiles():
                if image is None:
                    continue

                tile_rect = pygame.Rect(
                    col * tile_size,
                    row * tile_size,
                    tile_size,
                    tile_size
                )

                if enemy_rect.colliderect(tile_rect):
                    tile_cx = tile_rect.centerx
                    tile_cy = tile_rect.centery

                    # direction vector from tile → enemy
                    vx = enemy_cx - tile_cx
                    vy = enemy_cy - tile_cy

                    # normalize
                    length = math.hypot(vx, vy)
                    if length != 0:
                        vx /= length
                        vy /= length

                    # apply knockback purely via vector
                    enemy.vx = vx * KNOCKBACK
                    enemy.vy = vy * KNOCKBACK

                    # prevent enemy from entering collision tiles by adjusting position
                    # calculate the minimum distance needed to move the enemy out of the tile
                    overlap_x = (enemy_rect.width + tile_rect.width) / 2 - abs(enemy_cx - tile_cx)
                    overlap_y = (enemy_rect.height + tile_rect.height) / 2 - abs(enemy_cy - tile_cy)

                    # move the enemy in the direction of least resistance
                    if overlap_x < overlap_y:
                        if enemy_cx < tile_cx:
                            enemy.x -= overlap_x
                        else:
                            enemy.x += overlap_x
                    else:
                        if enemy_cy < tile_cy:
                            enemy.y -= overlap_y
                        else:
                            enemy.y += overlap_y

                    # update the enemy's hitbox if it has an update_hitbox method
                    if hasattr(enemy, 'update_hitbox'):
                        enemy.update_hitbox()

                    break

    def draw_collision_tiles(self, surface: pygame.Surface) -> None:
        tile_size = self.tile_size
        window_height = GlobalConstants.GAMEPLAY_HEIGHT

        layer = self.tiled_map.get_layer_by_name("collision")

        for col, row, image in layer.tiles():
            if image is None:
                continue
            world_y = row * tile_size
            screen_y = world_y - self.camera_y
            if screen_y + tile_size < 0 or screen_y > window_height:
                continue
            surface.blit(image, (col * tile_size, screen_y))


    def fire_all_weapons(self,state):
        def has_active(self, weapon_name: str) -> bool:
            return any(b.weapon_name == weapon_name for b in self.player_bullets)

        # -------------------------
        # MACHINE GUN
        # -------------------------
        if self.controller.main_weapon_button and not self.playerDead:
            self.player_bullets.extend(
                self.starship.machine_gun.fire_machine_gun()
            )

        # -------------------------
        # PLAYER MISSILES
        # -------------------------
        if self.controller.fire_missiles and not self.playerDead:
            self.starship.missile.x = self.starship.x
            self.starship.missile.y = self.starship.y

            missile = self.starship.missile.fire_missile()
            if missile is not None:
                self.player_bullets.append(missile)

        # -------------------------
        # BUSTER CANNON
        # -------------------------
        if state.starship.equipped_magic[0] == "Buster Cannon" and not self.playerDead:
            if self.controller.magic_1_button:
                if not state.starship.buster_cannon.is_charging:
                    state.starship.buster_cannon.start_charge()
                state.starship.buster_cannon.update()
            elif state.starship.buster_cannon.is_charging:
                self.player_bullets.extend(
                    state.starship.buster_cannon.fire_buster_cannon()
                )

        # -------------------------
        # PLASMA BLASTER (single beam)
        # -------------------------
        if state.starship.equipped_magic[0] == "Plasma Blaster" and not self.playerDead:
            if self.controller.magic_1_button and not has_active(self, "Plasma Blaster"):
                plasma = state.starship.plasma_blaster.fire_plasma_blaster()
                if plasma is not None:
                    self.player_bullets.append(plasma)

        # -------------------------
        # ENERGY BALL (ROF internal)
        # -------------------------
        if state.starship.equipped_magic[0] == "Energy Ball" and not self.playerDead:
            if self.controller.magic_1_button:
                energy_ball = state.starship.energy_ball.fire_energy_ball(self.controller)
                if energy_ball is not None:
                    self.player_bullets.append(energy_ball)

        # -------------------------
        # METAL SHIELD (single)
        # -------------------------
        if state.starship.equipped_magic[0] == "Metal Shield" and not self.playerDead:
            if self.controller.magic_1_button and not has_active(self, "Metal Shield"):
                shield = state.starship.metal_shield.fire_metal_shield()
                if shield is not None:
                    self.player_bullets.append(shield)

        # -------------------------
        # NAPALM SPREAD
        # -------------------------
        if state.starship.equipped_magic[0] == "Napalm Spread" and not self.playerDead:
            if self.controller.magic_1_button:
                napalm = state.starship.napalm_spread.fire_napalm_spread()
                if napalm is not None:
                    self.player_bullets.append(napalm)

        # -------------------------
        # BEAM SABER (single, held)
        # -------------------------
        if state.starship.equipped_magic[0] == "Beam Saber" and not self.playerDead:
            if self.controller.magic_1_button and not has_active(self, "Beam Saber"):
                saber = state.starship.beam_saber.fire_beam_saber()
                if saber is not None:
                    self.player_bullets.append(saber)

        if not self.controller.magic_1_button:
            self.player_bullets[:] = [
                b for b in self.player_bullets if b.weapon_name != "Beam Saber"
            ]

        # -------------------------
        # WAVE CRASH
        # -------------------------
        if state.starship.equipped_magic[0] == "Wave Crash" and not self.playerDead:
            if self.controller.magic_1_button:
                self.player_bullets.extend(
                    state.starship.wave_crash.fire_wave_crash()
                )

        # -------------------------
        # WIND SLICER
        # -------------------------
        if state.starship.equipped_magic[0] == "Wind Slicer" and not self.playerDead:
            if self.controller.magic_1_button:
                self.player_bullets.extend(
                    state.starship.wind_slicer.fire_wind_slicer()
                )


    def weapon_helper(self, state=None):
        for bullet in list(self.player_bullets):

            # --- movement / positioning ---
            if bullet.weapon_name == "Missile":
                if getattr(bullet, "target_enemy", None) is None and hasattr(self, "get_nearest_enemy"):
                    bullet.target_enemy = self.get_nearest_enemy(state, bullet)
                bullet.update()

            elif bullet.weapon_name == "Metal Shield":
                bullet.update_orbit(
                    self.starship.x + self.starship.width / 2,
                    self.starship.y + self.starship.height / 2
                )

            elif bullet.weapon_name == "Beam Saber":
                bullet.x = self.starship.x + self.starship.width // 2
                bullet.y = self.starship.y - 20
                bullet.update()

            else:
                bullet.update()

            # 🔴 CRITICAL: rect must always be updated AFTER movement
            bullet.update_rect()


    def metal_shield_helper(self):
        for bullet in list(self.player_bullets):

            if bullet.weapon_name == "Metal Shield":
                continue  # never auto-remove shield

            screen_x = bullet.x - getattr(self.camera, "x", 0)
            screen_y = bullet.y - self.camera.y

            off_screen = (
                    screen_y + bullet.height < 0 or
                    screen_y > (self.window_height / self.camera.zoom) or
                    screen_x + bullet.width < 0 or
                    screen_x > (self.window_width / self.camera.zoom)
            )

            if off_screen or not getattr(bullet, "is_active", True):
                self.player_bullets.remove(bullet)


    def rect_helper(self, state):
        ui_panel_rect = pygame.Rect(
            0,
            GlobalConstants.GAMEPLAY_HEIGHT,
            GlobalConstants.BASE_WINDOW_WIDTH,
            GlobalConstants.UI_PANEL_HEIGHT
        )

        for enemy in list(state.enemies):
            # Convert enemy position to screen coordinates
            enemy_screen_y = enemy.y - self.camera.y

            # Create enemy rect in screen coordinates
            enemy_rect = pygame.Rect(
                enemy.x,
                enemy_screen_y,
                enemy.width,
                enemy.height
            )

            # Check if enemy intersects with UI panel
            if enemy_rect.colliderect(ui_panel_rect):
                # Set enemy health to zero and is_active to False to ensure it's removed and not drawn
                enemy.enemyHealth = 0
                enemy.is_active = False
                self.remove_enemy_if_dead(enemy, state)

    def bullet_collision_helper_remover(self, state):
        for bullet in list(self.enemy_bullets):
            bullet.update()

            # Call lay_bomb in UPDATE mode for each bullet
            for enemy in state.enemies:
                if hasattr(enemy, "lay_bomb"):
                    enemy.lay_bomb(bullet=bullet, state=state)

            # Increase the buffer zone to ensure bullets have more time to appear on screen
            world_top_delete = self.camera.y - 500
            # Adjust for camera zoom to get correct world coordinates and increase buffer
            world_bottom_delete = self.camera.y + (self.window_height / self.camera.zoom) + 500

            # Debug print to help diagnose the issue
            # print(f"[BULLET CHECK] bullet.y={bullet.y:.1f}, camera.y={self.camera.y:.1f}, world_bottom_delete={world_bottom_delete:.1f}")

            if bullet.y < world_top_delete or bullet.y > world_bottom_delete:
                # print(f"[DELETE BULLET] y={bullet.y:.1f}, cam_y={self.camera.y:.1f}, reason: {'above' if bullet.y < world_top_delete else 'below'}")
                self.enemy_bullets.remove(bullet)
                continue

            # Collision check
            if bullet.collide_with_rect(self.starship.hitbox):
                self.starship.shipHealth -= bullet.damage
                bullet.is_active = False
                self.enemy_bullets.remove(bullet)





    def collision_tile_helper(self, state):
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

        # -------------------------
        # ENEMY BODY COLLISION DAMAGE (GLOBAL RULE)
        # -------------------------
        player_rect = self.starship.hitbox

        if not self.starship.invincible:
            # TODO this MUST be reading from current_level.enemies or something, not
            # checking every f'n enemy every single time

            for enemy in state.enemies:
                # Skip coins - they should not hurt the player when touched
                if hasattr(enemy, "__class__") and enemy.__class__.__name__ == "Coins":
                    continue

                enemy_rect = pygame.Rect(
                    enemy.x,
                    enemy.y,
                    enemy.width,
                    enemy.height
                )

                if player_rect.colliderect(enemy_rect):
                    self.starship.shipHealth -= 10
                    self.starship.on_hit()
                    break  # ⛔ only one hit per frame

    def draw_sub_weapon_rect_helper(self,state):
        zoom = self.camera.zoom

        for bullet in self.player_bullets:
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * zoom)
            bh = int(bullet.height * zoom)
            rect = pygame.Rect(bx, by, bw, bh)

            # ---- visual by capability / type ----
            if hasattr(bullet, "area_of_effect_x"):  # Napalm
                if getattr(bullet, "has_exploded", False):
                    aoe_w = int(bullet.area_of_effect_x * zoom)
                    aoe_h = int(bullet.area_of_effect_y * zoom)
                    aoe_rect = pygame.Rect(
                        bx - aoe_w // 2,
                        by - aoe_h // 2,
                        aoe_w,
                        aoe_h
                    )
                    pygame.draw.rect(state.DISPLAY, (255, 80, 0), aoe_rect, 4)
                else:
                    pygame.draw.rect(state.DISPLAY, (255, 100, 0), rect)

            elif hasattr(bullet, "update_orbit"):  # Metal Shield
                pygame.draw.rect(state.DISPLAY, (128, 0, 128), rect)

            elif hasattr(bullet, "target_enemy"):  # Missile
                pygame.draw.rect(state.DISPLAY, (128, 0, 128), rect)

            elif bullet.weapon_name == "Buster Cannon":
                pygame.draw.rect(state.DISPLAY, (255, 255, 255), rect)
                pygame.draw.rect(
                    state.DISPLAY,
                    (255, 255, 0),
                    (bx - 2, by - 2, bw + 4, bh + 4),
                    5
                )

            elif bullet.weapon_name == "Wind Slicer":
                pygame.draw.rect(state.DISPLAY, (180, 220, 255), rect)

            elif bullet.weapon_name == "Energy Ball":
                pygame.draw.rect(state.DISPLAY, (0, 200, 255), rect)

            elif bullet.weapon_name == "Wave Crash":
                pygame.draw.rect(state.DISPLAY, (0, 255, 0), rect)

            elif bullet.weapon_name == "Plasma Blaster":
                pygame.draw.rect(state.DISPLAY, (0, 255, 255), rect)

            else:  # default (machine gun, etc.)
                pygame.draw.rect(state.DISPLAY, (255, 255, 0), rect)

            pygame.draw.rect(state.DISPLAY, (255, 255, 0), rect, 1)
