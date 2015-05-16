from copy import deepcopy
import random
import datetime

from browser import document, timer


class Gol:
    def __init__(self):
        self.canvas = document["my-canvas"]
        self.ctx = self.canvas.getContext("2d")
        #self.ctx.translate(.5, .5)

        self.is_active = False
        self.in_tick = False

        self.grid = []
        self.initial_state = []
        self.tick_count = 0
        self.dead = 0
        self.alive = 0

        self.line_width = 1
        self.alive_cell_color = "#00FF00"
        self.dead_cell_color = "#e5e5e5"
        self.blank_cell_color = "#FFFFFF"
        self.grid_color = "#808080"

        self.init_grid()
        self.update_canvas()

        document["btn_start_stop"].disabled = "disabled"
        document["btn_tick"].disabled = "disabled"
        document["btn_clear"].disabled = "disabled"

    def init_grid(self, ev=None):
        print(">> init_grid", datetime.datetime.utcnow())

        self.cols = int(document["edt_cols"].value)
        self.rows = int(document["edt_rows"].value)
        self.size = int(document["edt_size"].value)
        self.seed_ratio = int(document["edt_seed"].value)

        #Rule is defined as S/B notation.
        #Some well-known rules :
        #23/3       : Conway's game of life
        #1234/3     : Mazetric
        #12345/3    : Maze
        #For more info : http://www.conwaylife.com/wiki/Cellular_automaton
        self.rule = document["edt_rule"].value

        self.tick_count = 0

        self.canvas.width = self.cols * self.size
        self.canvas.height = self.rows * self.size

        document["btn_start_stop"].disabled = "disabled"
        document["btn_tick"].disabled = "disabled"
        document["btn_clear"].disabled = "disabled"

        self.grid = [[0 for x in range(self.cols)] for y in range(self.rows)]
        print("<< init_grid", datetime.datetime.utcnow())

    def put_rect(self, rw, cl, color):
        x1 = cl * self.size
        y1 = rw * self.size

        self.ctx.fillStyle = color
        self.ctx.fillRect(x1, y1, self.size, self.size)

    def update_canvas(self):
        self.dead = 0
        self.alive = 0

        print(">> update_canvas", datetime.datetime.utcnow())
        rw = 0
        while rw < self.rows:
            cl = 0
            while cl < self.cols:
                if self.grid[rw][cl]:
                    color = self.alive_cell_color
                    self.alive += 1
                else:
                    color = self.dead_cell_color
                    self.dead += 1

                self.put_rect(rw, cl, color)

                cl = cl + 1
            rw = rw + 1

        self.update_labels()
        print("<< update_canvas", datetime.datetime.utcnow())

    def seed(self, ev):
        print(">> seed", datetime.datetime.utcnow())

        self.init_grid()

        for rw in range(self.rows):
            for cl in range(self.cols):

                seed_chance = random.randint(1, 100)

                if seed_chance <= self.seed_ratio:
                    self.grid[rw][cl] = 1
                else:
                    self.grid[rw][cl] = 0 #empty cell

        self.update_canvas()

        document["btn_start_stop"].disabled = ""
        document["btn_tick"].disabled = ""
        document["btn_clear"].disabled = ""

        self.initial_state = deepcopy(self.grid)
        print("<< seed", datetime.datetime.utcnow())

    def start_stop(self, ev):
        if self.is_active:
            self.is_active = False
            document["btn_start_stop"].text = "Start"

            document["btn_start_stop"].disabled = ""
            document["btn_tick"].disabled = ""
            document["btn_clear"].disabled = ""
        else:
            self.tick_delay = int(document["edt_delay"].value)
            self.is_active = True
            document["btn_start_stop"].text = "Stop"

            document["btn_start_stop"].disabled = ""
            document["btn_tick"].disabled = "disabled"
            document["btn_clear"].disabled = "disabled"

            self.tick()
            timer.set_timeout(self.tick, self.tick_delay)

    def update_labels(self):
        document["lbl_tickno"].text = "Round: %d" %(self.tick_count)
        document["lbl_alive"].text = "Alive: %d" %(self.alive)
        document["lbl_dead"].text = "Dead: %d" %(self.dead)

    def tick(self, ev=None):
        if self.in_tick:
            return

        self.in_tick = True

        self.alive = 0
        self.dead = 0

        #because slicing does not copy if a list is contained in a list !
        old_grid = deepcopy(self.grid)

        _sr, _br = self.rule.split('/')
        _sr = [int(x) for x in _sr]
        _br = [int(x) for x in _br]

        rw = 0
        while rw < self.rows:
            cl = 0
            while cl < self.cols:
                n_alive = 0

                for x in range(-1, 2):
                    for y in range(-1, 2):
                        nx = cl + x
                        ny = rw + y

                        if nx < 0:
                            nx = self.cols - 1
                        if ny < 0:
                            ny = self.rows - 1

                        if (nx >= 0) and (ny >= 0) and (nx < self.cols) and (ny < self.rows) and ((x != 0) or (y != 0)):
                            if old_grid[ny][nx] == 1:
                                n_alive += 1

                if self.grid[rw][cl] == 1:
                    #if cell is alive !
                    if not(n_alive in _sr):
                        self.grid[rw][cl] = 0
                else:
                    if n_alive in _br:
                        self.grid[rw][cl] = 1

                cl = cl + 1
            rw = rw + 1

        self.in_tick = False
        self.tick_count += 1

        self.update_canvas()

        if self.is_active:
            timer.set_timeout(self.tick, self.tick_delay)


gol = Gol()

document['btn_seed'].bind('click', gol.seed)
document['btn_start_stop'].bind('click', gol.start_stop)
document['btn_tick'].bind('click', gol.tick)
document['btn_clear'].bind('click', gol.init_grid)
