from copy import deepcopy
import random
import datetime

from browser import document, timer

canvas = document["my-canvas"]
ctx = canvas.getContext("2d")
#self.ctx.translate(.5, .5)
fillRect = ctx.fillRect

is_active = False
in_tick = False

grid = []
initial_state = []
tick_count = 0
dead = 0
alive = 0

line_width = 1
alive_cell_color = "#00FF00"
dead_cell_color = "#e5e5e5"
blank_cell_color = "#FFFFFF"
grid_color = "#808080"

document["btn_start_stop"].disabled = "disabled"
document["btn_tick"].disabled = "disabled"
document["btn_clear"].disabled = "disabled"

cols, rows, size, seed_ratio, rule, dead, alive, tick_delay = 0, 0, 0, 0, 0, 0, 0, 0

def init_grid(ev=None):
    global cols, rows, size, seed_ratio, rule, canvas, tick_count, grid
    print(">> init_grid", datetime.datetime.utcnow())

    cols = int(document["edt_cols"].value)
    rows = int(document["edt_rows"].value)
    size = int(document["edt_size"].value)
    seed_ratio = int(document["edt_seed"].value)

    #Rule is defined as S/B notation.
    #Some well-known rules :
    #23/3       : Conway's game of life
    #1234/3     : Mazetric
    #12345/3    : Maze
    #For more info : http://www.conwaylife.com/wiki/Cellular_automaton
    rule = document["edt_rule"].value

    tick_count = 0

    canvas.width = cols * size
    canvas.height = rows * size

    document["btn_start_stop"].disabled = "disabled"
    document["btn_tick"].disabled = "disabled"
    document["btn_clear"].disabled = "disabled"

    grid = [[0 for x in range(cols)] for y in range(rows)]
    print("<< init_grid", datetime.datetime.utcnow())

def update_canvas():
    global dead, alive
    dead = 0
    alive = 0

    print(">> update_canvas", datetime.datetime.utcnow())
    rw = 0
    for rw in range(rows):
        for cl in range(cols):
            if grid[rw][cl]:
                color = alive_cell_color
                alive += 1
            else:
                color = dead_cell_color
                dead += 1

            x1 = cl * size
            y1 = rw * size
            ctx.fillStyle = color
            fillRect(x1, y1, size, size)

    update_labels()
    print("<< update_canvas", datetime.datetime.utcnow())

def seed(ev):
    global initial_state, alive, dead
    
    print(">> seed", datetime.datetime.utcnow())

    init_grid()
    
    alive = 0

    for rw in range(rows):
        for cl in range(cols):

            seed_chance = random.randint(1, 100)

            if seed_chance <= seed_ratio:
                grid[rw][cl] = 1
                alive += 1
                color = alive_cell_color
            else:
                grid[rw][cl] = 0 #empty cell
                color = dead_cell_color
            x1 = cl * size
            y1 = rw * size
            ctx.fillStyle = color
            fillRect(x1, y1, size, size)
            
    dead = (rows * cols) - alive
    update_labels()

    document["btn_start_stop"].disabled = ""
    document["btn_tick"].disabled = ""
    document["btn_clear"].disabled = ""

    initial_state = deepcopy(grid)
    print("<< seed", datetime.datetime.utcnow())

def start_stop(ev):
    global is_active, tick_delay
    if is_active:
        is_active = False
        document["btn_start_stop"].text = "Start"

        document["btn_start_stop"].disabled = ""
        document["btn_tick"].disabled = ""
        document["btn_clear"].disabled = ""
    else:
        tick_delay = int(document["edt_delay"].value)
        is_active = True
        document["btn_start_stop"].text = "Stop"

        document["btn_start_stop"].disabled = ""
        document["btn_tick"].disabled = "disabled"
        document["btn_clear"].disabled = "disabled"

        tick()
        timer.set_timeout(tick, tick_delay)

def update_labels():
    document["lbl_tickno"].text = "Round: %d" %(tick_count)
    document["lbl_alive"].text = "Alive: %d" %(alive)
    document["lbl_dead"].text = "Dead: %d" %(dead)

def tick(ev=None):
    global in_tick, alive, dead, tick_count

    if in_tick:
        return

    in_tick = True

    alive = 0
    dead = 0

    #because slicing does not copy if a list is contained in a list !
    old_grid = deepcopy(grid)
    
    _sr, _br = rule.split('/')
    _sr = [int(x) for x in _sr]
    _br = [int(x) for x in _br]

    for rw in range(rows):
        for cl in range(cols):
            n_alive = 0

            for x in range(-1, 2):
                nx = cl + x
                if nx < 0:
                    nx = cols - 1
                elif nx >= cols:
                    continue

                for y in range(-1, 2):
                    ny = rw + y

                    if ny < 0:
                        ny = rows - 1

                    if (ny < rows) and ((x != 0) or (y != 0)):
                        if old_grid[ny][nx] == 1:
                            n_alive += 1

            if grid[rw][cl] == 1:
                #if cell is alive !
                if not(n_alive in _sr):
                    grid[rw][cl] = 0
                    dead += 1
                    x1 = cl * size
                    y1 = rw * size
                    ctx.fillStyle = dead_cell_color
                    fillRect(x1, y1, size, size)
            else:
                if n_alive in _br:
                    grid[rw][cl] = 1
                    x1 = cl * size
                    y1 = rw * size
                    ctx.fillStyle = alive_cell_color
                    fillRect(x1, y1, size, size)
                else:
                    dead += 1

    alive = (rows * cols) - dead
    in_tick = False
    tick_count += 1

    update_labels()

    if is_active:
        timer.set_timeout(tick, tick_delay)

init_grid()
update_canvas()

document['btn_seed'].bind('click', seed)
document['btn_start_stop'].bind('click', start_stop)
document['btn_tick'].bind('click', tick)
document['btn_clear'].bind('click', init_grid)
