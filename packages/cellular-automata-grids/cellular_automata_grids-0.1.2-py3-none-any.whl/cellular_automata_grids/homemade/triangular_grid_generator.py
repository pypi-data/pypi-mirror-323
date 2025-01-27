import math


class TriangularGridGenerator:
    @staticmethod
    def set_up_grid(cell_size: int, rows: int, cols: int):
        triangle_height = cell_size * math.sin(math.pi / 3)
        half_cell_size = cell_size / 2
        height = rows * triangle_height
        width = (cols + 1) * half_cell_size

        return height, width, cell_size, half_cell_size, triangle_height

    @staticmethod
    def generate_points(row, col, cell_size, half_cell_size, triangle_height):
        x, y = col * half_cell_size, row * triangle_height

        pointing_up = [
            (x, y + triangle_height),
            (x + cell_size, y + triangle_height),
            (x + half_cell_size, y),
        ]

        pointing_down = [
            (x, y),
            (x + cell_size, y),
            (x + half_cell_size, y + triangle_height),
        ]

        coords_map = [
            [pointing_up, pointing_down],
            [pointing_down, pointing_up],
        ]

        return coords_map[row % 2][col % 2]
