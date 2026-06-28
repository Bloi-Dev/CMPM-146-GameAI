from heapq import heappush, heappop
from math import sqrt


def find_path(source_point, destination_point, mesh):

    """
    Searches for a path from source_point to destination_point through the mesh

    Args:
        source_point: starting point of the pathfinder
        destination_point: the ultimate goal the pathfinder must reach
        mesh: pathway constraints the path adheres to

    Returns:

        A path (list of points) from source_point to destination_point if exists
        A list of boxes explored by the algorithm
    """

    path = []

    source_box = find_boxes(source_point, mesh["boxes"])
    destination_box = find_boxes(destination_point, mesh["boxes"])

    if source_box is None or destination_box is None:
        print("No path!")
        return path, []

    if source_box == destination_box:
        return [source_point, destination_point], [source_box]

    queue = []

    forward_dist = {source_box: 0}
    backward_dist = {destination_box: 0}

    forward_prev = {}
    backward_prev = {}

    forward_detail = {source_box: source_point}
    backward_detail = {destination_box: destination_point}

    boxes = {
        source_box: True,
        destination_box: True
    }

    heappush(queue, (0, source_box, "forward"))
    heappush(queue, (0, destination_box, "backward"))

    meeting_box = None

    while queue:
        priority, current_box, direction = heappop(queue)

        if direction == "forward":
            dist = forward_dist
            prev = forward_prev
            detail = forward_detail

            other_dist = backward_dist
            goal_point = destination_point
        else:
            dist = backward_dist
            prev = backward_prev
            detail = backward_detail

            other_dist = forward_dist
            goal_point = source_point

        boxes[current_box] = True

        if current_box in other_dist:
            meeting_box = current_box
            break

        for neighbor in mesh["adj"][current_box]:
            new_detail_point = clamp_point_to_box(
                detail[current_box],
                neighbor
            )

            new_distance = dist[current_box] + distance(
                detail[current_box],
                new_detail_point
            )

            if neighbor not in dist or new_distance < dist[neighbor]:
                dist[neighbor] = new_distance
                prev[neighbor] = current_box
                detail[neighbor] = new_detail_point
                boxes[neighbor] = True

                heuristic = distance(new_detail_point, goal_point)

                heappush(
                    queue,
                    (new_distance + heuristic, neighbor, direction)
                )

    # Debug Statements
    # print("Forward visited:", len(forward_dist))
    # print("Backward visited:", len(backward_dist))
    # print("Meeting box:", meeting_box)

    if meeting_box is None:
        print("No path!")
        return [], boxes.keys()

    forward_boxes = []
    current = meeting_box

    while current != source_box:
        forward_boxes.append(current)
        current = forward_prev[current]

    forward_boxes.append(source_box)
    forward_boxes.reverse()

    backward_boxes = []
    current = meeting_box

    while current != destination_box:
        current = backward_prev[current]
        backward_boxes.append(current)

    full_boxes = forward_boxes + backward_boxes

    path = [source_point]
    current_point = source_point

    for box in full_boxes[1:]:
        current_point = clamp_point_to_box(current_point, box)
        path.append(current_point)

    path[-1] = destination_point

    return path, boxes.keys()


def find_boxes(point, boxes):
    px, py = point

    for box in boxes:
        x1, x2, y1, y2 = box

        if x1 <= px <= x2 and y1 <= py <= y2:
            return box

    return None


def clamp(value, lower, upper):
    return max(lower, min(value, upper))


def clamp_point_to_box(point, box):
    px, py = point
    x1, x2, y1, y2 = box

    return (
        clamp(px, x1, x2),
        clamp(py, y1, y2)
    )


def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)