import numpy as np

def is_on_line(x1, y1, x2, y2, x, y):
    """ Check if (x, y) is on the line defined by (x1, y1) and (x2, y2) """
    if x <= max(x1, x2) and x >= min(x1, x2) and y <= max(y1, y2) and y >= min(y1, y2):
        return True
    return False

def line_intersection(line1, line2):
    """ Check if two lines intersect """
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    # Calculate the determinants
    det1 = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    det2 = (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
    det3 = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)

    if det1 == 0:  # Lines are parallel
        return False

    # Intersection point
    px = det2 / det1
    py = det3 / det1

    # Check if intersection point is on both segments
    if is_on_line(x1, y1, x2, y2, px, py) and is_on_line(x3, y3, x4, y4, px, py):
        return True
    else:
        return False

def bounding_box_line_collision(box, line):
    """ Check if a bounding box collides with a line """
    x_min, y_min, x_max, y_max = box
    # Define the edges of the bounding box
    top_edge = (x_min, y_min, x_max, y_min)
    bottom_edge = (x_min, y_max, x_max, y_max)
    left_edge = (x_min, y_min, x_min, y_max)
    right_edge = (x_max, y_min, x_max, y_max)

    # Check if the line intersects any of the edges
    if (line_intersection(line, top_edge) or line_intersection(line, bottom_edge) or
        line_intersection(line, left_edge) or line_intersection(line, right_edge)):
        return True
    return False

def point_position_relative_to_line(line, bbox):
    """
    Determine the position of a point relative to a line.
    Returns -1 if the point is on the left side, 1 if on the right side, or 0 if on the line.
    """
    # Calculate the center of the bounding box
    center_x = (bbox[0] + bbox[2]) // 2
    center_y = (bbox[1] + bbox[3]) // 2
    point = (center_x, center_y)
    x1, y1, x2, y2 = line
    x, y = point

    # Calculate the determinant
    # (x1, y1) and (x2, y2) define the line, (x, y) is the point
    det = (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1)

    if det > 0:
        return 1  # Point is on the right side
    elif det < 0:
        return -1 # Point is on the left side
    return 0       # Point is on the line


