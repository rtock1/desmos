from PIL import Image
from functools import cmp_to_key
import interface


# --- INITIALIZING VARIABLES AND FUNCTIONS --- #
im = Image.open("Image Rendering/suki_25.png")

width = im.width
height = im.height
print("Width: " + str(width) + ", Height: " + str(height))

f = open("../randompy/desmos_output.txt", "w")

neighbors_all = {(x, y) for x in range(-1, 2) for y in range(-1, 2) if x != 0 or y != 0}
neighbors_adjacent = {(x, y) for x in range(-1, 2) for y in range(-1, 2) if (x == 0) != (y == 0)}


def add_tuple(a, b):
    to_return = (a[0] + b[0], a[1] + b[1])
    return to_return


def flood_fill(point, colors, diagonals=False):
    found_points = set()
    queue = [point]
    found_points.add(point)
    while len(queue) > 0:
        point = queue.pop(0)
        neighbors = neighbors_all if diagonals else neighbors_adjacent
        next_points = {add_tuple(point, n) for n in neighbors}
        for p in next_points:
            if p[0] < 0 or p[0] >= width:
                continue
            if p[1] < 0 or p[1] >= height:
                continue
            if im.getpixel(p) in colors:
                if p not in found_points:
                    queue.append(p)
                    found_points.add(p)

    return found_points


def get_neighboring_points(point, diagonals=False):
    neighbors = neighbors_all if diagonals else neighbors_adjacent
    return {add_tuple(point, n) for n in neighbors}


def next_point(point, edge_points, edge, right=True):
    rotate_dir = not right
    working_point = point
    move_dir = rotate(edge, rotate_dir)

    if add_tuple(add_tuple(working_point, move_dir), edge) in edge_points:
        return_tuple = (rotate(edge, not rotate_dir), add_tuple(add_tuple(working_point, move_dir), edge))
    elif add_tuple(working_point, move_dir) in edge_points:
        return_tuple = (edge, add_tuple(working_point, move_dir))
    else:
        return_tuple = (rotate(edge, rotate_dir), working_point)

    return return_tuple


def rotate(point, left=True):
    if left:
        return_tuple = (-point[1], point[0])
    else:
        return_tuple = (point[1], -point[0])
    return return_tuple


def get_bounding_box_area(set_of_points):
    x = [n[0] for n in set_of_points]
    y = [n[1] for n in set_of_points]

    return (max(y) - min(y)) * (max(x) - min(x))


def compare(set1, set2):
    return get_bounding_box_area(set1[1]) - get_bounding_box_area(set2[1])


# --- FIND PATCHES OF THE SAME COLOR --- #
unseen_points = set()
image_colors = set()
for x in range(width):
    for y in range(height):
        unseen_points.add((x, y))
        image_colors.add(im.getpixel((x, y)))

patch_points = []
while len(unseen_points) > 0:
    curr_point = unseen_points.pop()
    curr_color = im.getpixel(curr_point)
    same_color_points = flood_fill(curr_point, {curr_color})
    patch_points.append((curr_color, same_color_points))
    unseen_points.difference_update(same_color_points)


# --- TRACE BOUNDARIES OF PATCHES --- #
boundary_points = []
for patch in patch_points:
    boundary = {n for n in patch[1] if len([j for j in get_neighboring_points(n) if j not in patch[1]]) > 0}
    boundary_points.append((patch[0], boundary))

move_right = True
ordered_boundaries = []
for boundary in boundary_points:
    points = list(boundary[1])
    max_y_index = -1
    max_y = -1
    for i in range(len(points)):
        if points[i][1] > max_y:
            max_y_index = i
            max_y = points[i][1]

    starting_point = ((0, 1), points[max_y_index])

    curr_point = starting_point
    boundary_ordered = [curr_point]
    while next_point(curr_point[1], boundary[1], curr_point[0], True) != starting_point:
        curr_point = next_point(curr_point[1], boundary[1], curr_point[0], True)
        boundary_ordered.append(curr_point)

    boundary_ordered = [n if n[0] != (0, 1) else (n[0], (n[1][0], n[1][1] + 1)) for n in boundary_ordered]
    boundary_ordered = [n if n[0] != (1, 0) else (n[0], (n[1][0] + 1, n[1][1] + 1)) for n in boundary_ordered]
    boundary_ordered = [n if n[0] != (0, -1) else (n[0], (n[1][0] + 1, n[1][1])) for n in boundary_ordered]

    ordered_boundaries.append((boundary[0], [n[1] for n in boundary_ordered]))


ordered_boundaries = sorted(ordered_boundaries, key=cmp_to_key(compare), reverse=True)
ordered_boundaries = [(n[0], [(j[0], height - j[1]) for j in n[1]]) for n in ordered_boundaries]

text = interface.Text()
text.set_text("The below folder contains ~3MB of image data and may lag your computer if opened")

folder = interface.Folder()
folder.set_collapsed(True)
folder.set_title("Image Data")

for i in ordered_boundaries:
    latex = "polygon("
    latex += str([n for n in i[1]])
    latex += ")"

    color = "rgb" + str(i[0][:3])

    expression = interface.Expression()
    expression.set_latex(latex)
    expression.set_color_latex(color)
    expression.set_line_width(1)
    expression.set_fill_opacity(1)

    folder.add_expression(expression)

graph = interface.Graph()
graph.reset_expressions()
graph.append(text)
graph.append(folder)
graph.generate_output("Image Rendering/output.txt")
