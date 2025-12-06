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
        self.map_scroll_speed_per_frame: float = 2

        self.bileSpitterGroup: list[BileSpitter] = []

        self.load_bile_spitters()





    def start(self, state) -> None:

        tile_size: int = self.tiled_map.tileheight
        map_width_tiles: int = self.tiled_map.width
        map_height_tiles: int = self.tiled_map.height

        # below is player position on map
        bottom_row: int = map_height_tiles - 180
        start_col: int = map_width_tiles // 20

        player_start_x: int = tile_size * start_col
        player_start_y: int = tile_size * bottom_row

        self.starship.x = player_start_x
        self.starship.y = player_start_y

        print(
            f"Starship start at: col={start_col}, row={bottom_row} | "
            f"x={self.starship.x}, y={self.starship.y}, map={map_width_tiles}x{map_height_tiles} tiles"
        )
        # print(
        #     f"Map = {self.map_width_tiles}x{self.map_height_tiles} tiles, "
        #     f"world height = {self.WORLD_HEIGHT}"
        # )
        # line camera up with player, clamped to world
        window_width, window_height = GlobalConstants.WINDOWS_SIZE

        # self.camera_y = max(
        #     0,
        #     min(
        #         self.starship.y - (window_height - self.starship.height),
        #         self.WORLD_HEIGHT - window_height,
        #     ),
        # )
        # self.camera.y = float(self.camera_y)

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

        # # 🔹 auto-scroll camera UP by move_screen_speed each frame
        # _, window_height = GlobalConstants.WINDOWS_SIZE
        #
        # max_camera_y: float = self.WORLD_HEIGHT - window_height
        # min_camera_y: float = 0.0
        #
        # self.camera_y -= self.move_screen_speed
        #
        # # clamp to world
        # if self.camera_y < min_camera_y:
        #     self.camera_y = min_camera_y
        # elif self.camera_y > max_camera_y:
        #     self.camera_y = max_camera_y
        #
        # # keep Camera object in sync
        # self.camera.y = float(self.camera_y)


    def draw(self, state):
        super().draw(state)
        # self.draw_tiled_background(state)

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

            if obj.properties.get("Type") == "bile_spitter":
                print("MATCH FOUND — Creating Bile Spitter!")
                enemy = BileSpitter()
                enemy.x = obj.x
                enemy.y = obj.y
                self.bileSpitterGroup.append(enemy)

        print("Bile spitter count =", len(self.bileSpitterGroup))
