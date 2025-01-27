import pygame
from . import BaseGrid
from ..homemade.triangular_grid_generator import TriangularGridGenerator


class TriangularGrid(BaseGrid):

    def set_up_window(self) -> None:
        rows, cols = len(self.automaton.grid), len(self.automaton.grid[0])

        self.height, self.width, self.cell_size, self.half_cell_size, self.triangle_height = (
            TriangularGridGenerator.set_up_grid(rows=rows, cols=cols, cell_size=self.tile_size)
        )

        self.screen: pygame.Surface = pygame.display.set_mode((self.width, self.height))

    def draw_grid(self) -> None:

        for y, row in enumerate(self.automaton.grid):
            for x, val in enumerate(row):
                pygame.draw.polygon(
                    surface=self.screen,
                    color=self.colors[val],
                    points=TriangularGridGenerator.generate_points(
                        row=y,
                        col=x,
                        cell_size=self.cell_size,
                        half_cell_size=self.half_cell_size,
                        triangle_height=self.triangle_height,
                    ),
                    width=0,
                )
