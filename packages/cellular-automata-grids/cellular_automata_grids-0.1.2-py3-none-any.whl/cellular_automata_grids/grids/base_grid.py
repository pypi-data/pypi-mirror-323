from abc import abstractmethod
from copy import deepcopy
import pygame


class BaseGrid:
    CAPTION_TPL: str = "{title} ({step})"

    @abstractmethod
    def set_up_window(self) -> None:
        """Needs to be implemented."""

    @abstractmethod
    def draw_grid(self) -> None:
        """Needs to be implemented."""

    def __init__(
        self,
        automaton,
        title: str = "Base Grid",
        tile_size: int = 1,
        run: bool = False,
        fps: int = 60,
        max_iteration: int = -1,
        colors: tuple = ("#000000", "#ffffff"),
        background: str | tuple[tuple[int, int, int]] = "#000000",
        select_every: int = 1,
    ):
        self.title = title
        self.step = 0
        self.animate: bool = run
        self.automaton = automaton
        self.initial_grid_state = deepcopy(self.automaton.grid)
        self.fps = fps
        self.max_iteration = max_iteration
        self.tile_size = tile_size
        self.colors = colors
        self.background = background
        self.select_every = select_every

        self.set_up_window()

    def __next__(self):

        if self.step % self.select_every == 0:
            self.draw_grid()

        if self.animate:
            self.make_a_step()

        # Update title and refresh the screen.
        pygame.display.update()
        pygame.display.set_caption(
            title=self.CAPTION_TPL.format(title=self.title, step=self.step),
        )

    def mainloop(self):
        pygame.init()
        self.run()

    def make_a_step(self, no_max: bool = False):
        if no_max or self.max_iteration < 0 or self.max_iteration > self.step:
            self.step += 1
            next(self.automaton)

    def reset_automaton(self):
        self.automaton.grid = deepcopy(self.initial_grid_state)
        self.step = 0

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                    running = False

                if event.type == pygame.KEYUP:
                    match event.key:
                        case pygame.K_SPACE:
                            self.animate = not self.animate
                        case pygame.K_s:
                            self.reset_automaton()
                        case pygame.K_RIGHT:
                            if not self.animate:
                                self.make_a_step(no_max=True)

            next(self)
            clock.tick(self.fps)
