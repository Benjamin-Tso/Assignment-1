import time
import numpy as np
import math
from gridgame import *
import random

##############################################################################################################################

# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.

# For your final submission, please set the GUI option to False.

# The gs argument controls the grid size. You should experiment with various sizes to ensure your code generalizes.
# Please do not modify or remove lines 18 and 19.

##############################################################################################################################

game = ShapePlacementGrid(GUI=False, render_delay_sec=0.001, gs=6, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##############################################################################################################################

# Initialization

# shapePos is the current position of the brush.

# currentShapeIndex is the index of the current brush type being placed (order specified in gridgame.py, and assignment instructions).

# currentColorIndex is the index of the current color being placed (order specified in gridgame.py, and assignment instructions).

# grid represents the current state of the board. 
    
    # -1 indicates an empty cell
    # 0 indicates a cell colored in the first color (indigo by default)
    # 1 indicates a cell colored in the second color (taupe by default)
    # 2 indicates a cell colored in the third color (veridian by default)
    # 3 indicates a cell colored in the fourth color (peach by default)

# placedShapes is a list of shapes that have currently been placed on the board.
    
    # Each shape is represented as a list containing three elements: a) the brush type (number between 0-8), 
    # b) the location of the shape (coordinates of top-left cell of the shape) and c) color of the shape (number between 0-3)

    # For instance [0, (0,0), 2] represents a shape spanning a single cell in the color 2=veridian, placed at the top left cell in the grid.

# done is a Boolean that represents whether coloring constraints are satisfied. Updated by the gridgames.py file.

##############################################################################################################################

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)


####################################################
# Timing your code's execution for the leaderboard.
####################################################

start = time.time()  # <- do not modify this.



##########################################
# Write all your code in the area below. 
##########################################


def find_random_pos(game):
    return (random.randint(0,game.gridSize-game.shapesDims[game.currentShapeIndex][0]), random.randint(0,game.gridSize-game.shapesDims[game.currentShapeIndex][1]))

def obj(a, b, c, game):
    return a * len(set([shape[2] for shape in game.placedShapes])) + b * len(set([shape[0] for shape in game.placedShapes])) + c * int(np.sum(game.grid == -1))

def keep_change(of1, of2, t):
    return of2 < of1 or random.random() < math.e ** ((of1-of2)/t)

def find_valid_color(game, shape_idx, pos):
    shape = game.shapes[shape_idx]
    x, y = pos
    covered = {(x + j, y + i)
               for i, row in enumerate(shape)
               for j, cell in enumerate(row) if cell}
    forbidden = set()
    for (cx, cy) in covered:
        for (nx, ny) in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
            if 0 <= nx < game.gridSize and 0 <= ny < game.gridSize and (nx, ny) not in covered:
                nc = game.grid[ny, nx]
                if nc != -1:
                    forbidden.add(int(nc))
    available = [c for c in range(len(game.colors)) if c not in forbidden]
    return random.choice(available) if available else None

def nav_to(game, x, y):
    if x < game.shapePos[0]:
        for i in range(game.shapePos[0]-x):
            game.execute("left")
    else:
        for i in range(x-game.shapePos[0]):
            game.execute("right")
    if y < game.shapePos[1]:
        for i in range(game.shapePos[1]-y):
            game.execute("up")
    else:
        for i in range(y-game.shapePos[1]):
            game.execute("down")

t = 0.7
bad_iterations = 0
iterations = 0
MAX_ITERATIONS = 5 ** game.gridSize
shape_cells = [int(s.sum()) for s in game.shapes]
while not game.checkGrid(game.grid) and iterations < MAX_ITERATIONS:
    iterations += 1
    progress = iterations / MAX_ITERATIONS
    shape_weights = [1.0 / (cells ** (5 * progress)) for cells in shape_cells]
    shape = random.choices(range(len(game.shapes)), weights=shape_weights, k=1)[0]
    while game.currentShapeIndex != shape:
        game.execute("switchshape")
    x, y = find_random_pos(game)
    color = find_valid_color(game, game.currentShapeIndex, (x, y))
    if color:
        initial_placed_shapes = list(game.placedShapes)
        nav_to(game, x, y)
        while game.currentColorIndex != color:
            game.execute("switchcolor")
        of1 = obj(1, 1, 25, game)
        game.execute("place")
        of2 = obj(1, 1, 25, game)
        t *=  0.99
        t = max(t, 0.001)
        _, _, _, _, placedShapes, _ = game.execute("export")
        if len(placedShapes) > len(initial_placed_shapes) and keep_change(of1, of2, t):
            bad_iterations = 0
            continue
        if len(placedShapes) != len(initial_placed_shapes):
            game.execute("undo")
    bad_iterations += 1
    if bad_iterations >= 200 or random.random() < 0.001: #random restart
        bad_iterations = 0
        t = 0.7
        while len(game.placedShapes) > 0:
            game.execute("undo")



########################################

# Do not modify any of the code below. 

########################################

end=time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end-start))
