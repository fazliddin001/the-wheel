import pygame as pg
from itertools import count, cycle
from functools import lru_cache
from random import randint, choice


@lru_cache(maxsize=1)
def bresenham_circle(radius):
    x = radius
    y = 0
    err = 0
    l1, l2, l3, l4, l5, l6, l7, l8 = [[] for _ in range(8)]

    while x >= y:
        l1.append((x, y))
        l2.append((y, x))
        l3.append((-y, x))
        l4.append((-x, y))
        l5.append((-x, -y))
        l6.append((-y, -x))
        l7.append((y, -x))
        l8.append((x, -y))

        y += 1
        err += 1 + 2*y
        if 2*(err-x) + 1 > 0:
            x -= 1
            err += 1 - 2*x

    return *l1, *l2[::-1], *l3, *l4[::-1], *l5, *l6[::-1], *l7, *l8[::-1]


class Ball:
    def __init__(self, surface: 'App'):
        self.surface = surface
        self.speed = randint(1, 6)
        self.percent_k = randint(200, 1000) / 1000
        self.circle = cycle(bresenham_circle(self.surface.default_radius))
        self.pos: tuple[float, float] = ...
        self.color = self.surface.default_color

        for i in range(randint(0, 10000)):
            next(self.circle)

    def draw(self):
        pg.draw.circle(self.surface.sc, self.color, self.pos, self.surface.ball_radius)
        pg.draw.aaline(self.surface.sc, (20, 20, 20), self.pos, self.surface.mouse_pos)

    def update(self):
        self.update_percent_k()
        _pos = [next(self.circle) for _ in range(self.speed)][0]
        _pos = self.surface.mouse_pos[0] + _pos[0], self.surface.mouse_pos[1] + _pos[1]

        self.pos = self.divide_segment(*self.surface.mouse_pos, *_pos, self.percent_k * self.surface.k_mul)

    @staticmethod
    def divide_segment(x1, y1, x2, y2, k) -> tuple[float, float]:
        x = (k * x2 + x1) / (k + 1)
        y = (k * y2 + y1) / (k + 1)
        return x, y

    def update_percent_k(self):
        self.percent_k += randint(0, 100) / 1000 * choice((1, -1)) * self.surface.smooth


class App:
    def __init__(self):
        pg.init()
        self.params = pg.display.Info()
        self.full_sc_size = self.params.current_w, self.params.current_h
        self.size = self.width, self.height = self.full_sc_size  # 800, 500
        self.sc = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()
        self.balls_count = 170
        self.ball_radius = 1.5
        self.default_radius = 400
        self.max_k_mul = 4
        self.k_mul = 0
        self.normal_k_mul = 1
        self.go_to_max = False
        self.default_color = [randint(0, 255) for _ in range(3)]
        self.balls = cycle([Ball(self) for _ in range(self.balls_count)])
        self.surface = pg.surface.Surface(self.size)
        self.surface.set_alpha(7)
        self.mouse_pos: tuple[int, int] = (0, 0)
        self.smooth = 0.013

    def run(self):
        for _ in count():
            [exit() for event in pg.event.get() if event.type == pg.QUIT]
            self.update_mouse_pos()
            self.handle_mouse()
            self.update_k_mul()

            pg.display.update()
            self.sc.blit(self.surface, (0, 0))

            for index, ball in enumerate(self.balls, 1):
                ball.update()
                ball.draw()
                if index == self.balls_count:
                    break

            self.clock.tick()
            pg.display.set_caption(str(self.clock.get_fps()))
            pg.display.flip()

    def update_mouse_pos(self):
        self.mouse_pos = pg.mouse.get_pos()

    def update_k_mul(self):
        if self.go_to_max:
            self.k_mul += self.smooth
            if self.k_mul > self.max_k_mul:
                self.k_mul = self.max_k_mul
                self.go_to_max = False

        else:
            if self.k_mul < self.normal_k_mul:
                self.k_mul += self.smooth
            elif self.k_mul > self.normal_k_mul:
                self.k_mul -= self.smooth

    def handle_mouse(self):
        pressed = pg.mouse.get_pressed()

        if pressed[-1]:
            self.k_mul -= self.smooth * 2
            if self.k_mul < 0:
                self.k_mul = 0

        elif pressed[0]:
            self.go_to_max = True


if __name__ == '__main__':
    App().run()
