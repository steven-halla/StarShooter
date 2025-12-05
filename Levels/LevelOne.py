import pygame
import pytmx

from Constants.GlobalConstants import GlobalConstants
from ScreenClasses.Camera import Camera
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelOne(VerticalBattleScreen):
    def __init__(self):
        super().__init__()

        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level1.tmx")

        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height







    def start(self, state) -> None:
        tile_size: int = self.tiled_map.tileheight
        map_width_tiles: int = self.tiled_map.width
        map_height_tiles: int = self.tiled_map.height

        # you can still tweak these later; leaving your current logic as-is
        bottom_row: int = map_height_tiles + 100
        start_col: int = map_width_tiles // 20

        player_start_x: int = tile_size * start_col
        player_start_y: int = tile_size * bottom_row

        self.starship.x = player_start_x
        self.starship.y = player_start_y

        print(
            f"Starship start at: col={start_col}, row={bottom_row} | "
            f"x={self.starship.x}, y={self.starship.y}, map={map_width_tiles}x{map_height_tiles} tiles"
        )

    def draw(self, state):
        super().draw(state)
        self.draw_tiled_background(state)

        # if not self.playerDead:
        #     self.starship.draw(state.DISPLAY)

        if not self.playerDead:
            zoom = self.camera.zoom

            ship_screen_x = self.camera.world_to_screen_x(self.starship.x)
            ship_screen_y = self.camera.world_to_screen_y(self.starship.y)

            ship_width = int(self.starship.width * zoom)
            ship_height = int(self.starship.height * zoom)

            ship_rect = pygame.Rect(
                ship_screen_x,
                ship_screen_y,
                ship_width,
                ship_height,
            )
            pygame.draw.rect(state.DISPLAY, self.starship.color, ship_rect)

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

        pygame.display.flip()

    def draw_tiled_background(self, state) -> None:
        tile_size = self.tile_size
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        bg_layer = self.tiled_map.get_layer_by_name("background")

        zoom = self.camera.zoom
        scaled_size = int(tile_size * zoom)

        for col, row, image in bg_layer.tiles():
            world_x = col * tile_size
            world_y = row * tile_size

            # 🔹 world -> screen using camera pattern we stole
            screen_x = self.camera.world_to_screen_x(world_x)
            screen_y = self.camera.world_to_screen_y(world_y)

            # cull if completely off-screen
            if screen_y + scaled_size < 0 or screen_y > window_height:
                continue

            scaled_image = pygame.transform.scale(image, (scaled_size, scaled_size))
            state.DISPLAY.blit(scaled_image, (screen_x, screen_y))
