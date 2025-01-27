import pygame
from . import BaseGrid


class SquareGrid(BaseGrid):

    def set_up_window(self) -> None:
        height, width = len(self.automaton), len(self.automaton[0])
        self.screen: pygame.Surface = pygame.Surface((width, height))
        self.window: pygame.Surface = pygame.display.set_mode(size=(width * self.tile_size, height * self.tile_size))

    def draw_grid(self) -> None:
        # Convert automaton grid to bitmap.
        pixel_array: pygame.PixelArray = pygame.PixelArray(self.screen)
        for y, row in enumerate(self.automaton):
            for x, val in enumerate(row):
                color = self.colors[val]
                pixel_array[x, y] = pygame.Color(color) if isinstance(color, str) else color
        pixel_array.close()

        # Adjust bitmap to screen size.
        self.window.blit(pygame.transform.scale(self.screen, self.window.get_rect().size), (0, 0))

        pygame.display.flip()
