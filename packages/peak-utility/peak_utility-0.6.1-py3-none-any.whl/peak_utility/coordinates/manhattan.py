def manhattan(point_1, point_2):
    """Calculates the Manhattan distance between two points."""
    x_1, y_1 = point_1
    x_2, y_2 = point_2
    return abs(x_1 - x_2) + abs(y_1 - y_2)
