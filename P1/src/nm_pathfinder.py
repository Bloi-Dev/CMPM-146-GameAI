from heapq import heappush, heappop
from math import sqrt

# Main Function:
# This function takes in the first click: 'source_point' and second click: 'destination_point'
# as well as 'mesh' the dict containing boxes and adjacency; then returns the shortest
# path from 'source_point' to 'destination_point'

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

    # Initialize the path as empty
    path = []

    # Finds which navmesh rectangle contains the starting point and destination point
    source_box = find_boxes(source_point, mesh["boxes"])
    destination_box = find_boxes(destination_point, mesh["boxes"])

    # Either click is outside all white walkable boxes, or there is no valid path
    # Print 'No path!'
    if source_box is None or destination_box is None:
        print("No path!")
        return path, []

    # If both points are inside the same box, search is not needed. The path is just a straight line from
    # source_point -> destination_point
    if source_box == destination_box:
        return [source_point, destination_point], [source_box]

    # Creates a prio queue for A*
    queue = []

    # forward_dist: starts from source box
    # backward_dist: starts from destination_box
    forward_dist = {source_box: 0}
    backward_dist = {destination_box: 0}

    # Store backpoints so we can reconstruct the paths later.
    forward_prev = {}
    backward_prev = {}

    # Store exact point inside each box where the path passes through
    forward_detail = {source_box: source_point}
    backward_detail = {destination_box: destination_point}

    # Keeps track of the explored/discovered boxes so the visualizer can color them
    boxes = {
        source_box: True,
        destination_box: True
    }

    # Starts both searches
    heappush(queue, (0, source_box, "forward"))
    heappush(queue, (0, destination_box, "backward"))

    # Store the first box where the two searches meet.
    meeting_box = None

    # Keep searching while boxes are aval. to explore.
    while queue:
        # Takes lowest prio item for queue
        priority, current_box, direction = heappop(queue)

        # If this item belongs to forward search, use the forward dict.
        if direction == "forward":
            dist = forward_dist
            prev = forward_prev
            detail = forward_detail

            # Check the backward search and see if it has reached this box
            other_dist = backward_dist
            goal_point = destination_point

        # Else this item belongs to the backward search, use the backward dict
        else:
            dist = backward_dist
            prev = backward_prev
            detail = backward_detail

            other_dist = forward_dist
            goal_point = source_point

        # Mark current box as explored
        boxes[current_box] = True

        # Stop early if both points have met
        if current_box in other_dist:
            meeting_box = current_box
            break

        #Expanding neighbors
        for neighbor in mesh["adj"][current_box]:
            new_detail_point = clamp_point_to_box(
                detail[current_box],
                neighbor
            )
            
            # legal point inside the neighbor box
            new_distance = dist[current_box] + distance(
                detail[current_box],
                new_detail_point
            )

            # Only updates if neighbor we have never reached it before
            # or we found a shorter way to reach it.
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
    # ---------------------------------------------- #
    # print("Forward visited:", len(forward_dist))
    # print("Backward visited:", len(backward_dist))
    # print("Meeting box:", meeting_box)

    # No connected path!
    if meeting_box is None:
        print("No path!")
        return [], boxes.keys()

    # Start rebuilding the forward path from the meeting box back to the source
    forward_boxes = []
    current = meeting_box

    # Follow the forward backpointers backward until reachig the source box
    while current != source_box:
        forward_boxes.append(current)
        current = forward_prev[current]

    # Add source box
    forward_boxes.append(source_box)
    forward_boxes.reverse()

    # Do the same for backward path
    backward_boxes = []
    current = meeting_box

    while current != destination_box:
        current = backward_prev[current]
        backward_boxes.append(current)

    # Combine both halves into one
    full_boxes = forward_boxes + backward_boxes

    # Start the path at the user's source click
    path = [source_point]
    current_point = source_point

    # Walkthrough each box in the box path.
    for box in full_boxes[1:]:
        current_point = clamp_point_to_box(current_point, box)
        path.append(current_point)

    # Replace the final clamped point with the actual clicked destination
    path[-1] = destination_point

    return path, boxes.keys()

# Helper Function: find_boxes:
# takes in a point, and the dict of boxes
# returns what box the point is in
def find_boxes(point, boxes):
    px, py = point

    for box in boxes:
        x1, x2, y1, y2 = box

        if x1 <= px <= x2 and y1 <= py <= y2:
            return box

    return None

# Helper function: clamp
# forces a numver to stay in range
def clamp(value, lower, upper):
    return max(lower, min(value, upper))

# Helper function: clamp_point_to_box
# Clamp the x- and y- coordinates and clamp it to the box's x- and y- range
# returns the closest legal point inside the box
def clamp_point_to_box(point, box):
    px, py = point
    x1, x2, y1, y2 = box

    return (
        clamp(px, x1, x2),
        clamp(py, y1, y2)
    )

# Helper function: distance
# Splits two points into x and y coords
# Calculate Euclidean distance and returns it.
def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)