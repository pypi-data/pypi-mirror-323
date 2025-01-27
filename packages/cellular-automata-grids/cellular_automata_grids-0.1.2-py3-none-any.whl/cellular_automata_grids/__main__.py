import secrets
import sys
from typing import Any
import click
from .grids import (
    SquareGrid,
    TriangularGrid,
    HexagonalGrid,
)
from cellular_automata_grids import settings

sys.path.insert(0, settings.BASE_DIR.as_posix())
from tests.test_utils import DemoAutomaton  # noqa: E402


grid_types: dict[str, Any] = {
    "square": SquareGrid,
    "hexagonal": HexagonalGrid,
    "triangular": TriangularGrid,
    "sqr": SquareGrid,
    "hex": HexagonalGrid,
    "tri": TriangularGrid,
    "s": SquareGrid,
    "h": HexagonalGrid,
    "t": TriangularGrid,
}

grid_types_names = list(grid_types.keys())


@click.command()
@click.option(
    "-t",
    "--grid-type",
    type=click.Choice(grid_types_names),
    default=grid_types_names[0],
    show_default=True,
    help="Select grid type.",
)
@click.option("-c", "--cols", default=33, show_default=True, help="Set grid number of cols.")
@click.option("-r", "--rows", default=20, show_default=True, help="Set grid number or rows.")
@click.option("-f", "--fps", default=10, show_default=True, help="Set grid number or rows.")
@click.option("-s", "--steps", default=-1, show_default=True, help="Number of steps to run.")
@click.option("-c", "--cell-size", default=48, show_default=True, help="Set grid cell size.")
@click.option("-x", "--run", default=False, is_flag=True, show_default=True, help="Run automaton processing on start.")
def main(grid_type: str, rows: int, steps: int, cols: int, run: bool, fps: int, cell_size: int):
    colors = (
        "red",
        "green",
        "yellow",
        "blue",
        "cyan",
        "magenta",
        "black",
        "white",
        "gray",
        "darkred",
        "pink",
        "darkgreen",
    )

    states = list(range(0, len(colors)))

    grid: list[list[int]] = []

    for row in range(rows):
        grid.append([])
        for _ in range(cols):
            grid[row].append(secrets.choice(states))

    automaton = DemoAutomaton(grid=grid, states=states)

    grid_types[grid_type](
        title=automaton.name,
        automaton=automaton,
        tile_size=cell_size,
        max_iteration=steps,
        fps=fps,
        run=run,
        colors=colors,
    ).mainloop()
