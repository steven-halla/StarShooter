import pygame
import pytmx

from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelOne(VerticalBattleScreen):
    def __init__(self):
        super().__init__()
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level1.tmx")

    # print("Ya;fdjaslfakf")




    def draw(self, state):
        # --- draw Tiled background layer "bg" ---
        if self.tiled_map.layers:
            tile_width = self.tiled_map.tilewidth
            tile_height = self.tiled_map.tileheight

            bg_layer = self.tiled_map.get_layer_by_name("background")

            for x, y, image in bg_layer.tiles():
                # no camera object yet, so just use tile coords
                pos_x = x * tile_width
                pos_y = y * tile_height

                scaled_image = pygame.transform.scale(
                    image,
                    (int(tile_width * 1.3), int(tile_height * 1.3))
                )

                state.DISPLAY.blit(scaled_image, (pos_x, pos_y))

        # --- then draw everything from the battle screen on top ---
        if not self.playerDead:
            self.starship.draw(state.DISPLAY)

        for enemy in self.bileSpitterGroup:
            enemy.draw(state.DISPLAY)

        for bullet in self.player_bullets:
            bullet.draw(state.DISPLAY)

        for bullet in self.enemy_bullets:
            bullet.draw(state.DISPLAY)

        pygame.display.flip()
