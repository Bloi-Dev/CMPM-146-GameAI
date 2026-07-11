
from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

num_nodes = 200
explore_faction = 2.

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """ Traverses the tree until the end criterion are met.
    e.g. find the best expandable node (node with untried action) if it exist,
    or else a terminal node

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 1 or 2

    Returns:
        node: A node from which the next stage of the search can proceed.
        state: The state associated with that node

    """
    while not board.is_ended(state) and len(node.untried_actions) == 0:
        is_opponent = board.current_player(state) != bot_identity


        best_action = None
        best_child = None
        best_score = float("-inf")

        for action, child in node.child_nodes.items():
            score = ucb(child, is_opponent)

            if score > best_score:
                best_score = score
                best_action = action
                best_child = child
        
        node = best_child
        state = board.next_state(state, best_action)

    return node, state

def expand_leaf(node: MCTSNode, board: Board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node (if it is non-terminal).

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:
        node: The added child node
        state: The state associated with that node

    """
    if board.is_ended(state):
        return node, state
    
    action = choice(node.untried_actions)
    node.untried_actions.remove(action)

    next_state = board.next_state(state, action)

    child = MCTSNode(
        parent = node,
        parent_action = action,
        action_list = board.legal_actions(next_state)
    )

    node.child_nodes[action] = child

    return child, next_state


def rollout(board: Board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.
    
    Returns:
        state: The terminal game state

    """
    while not board.is_ended(state):
        actions = board.legal_actions(state)
        player = board.current_player(state)
        

        # Upgraded Heuristic version
        # Take an immediate action winning move if avali
        for action in actions:
            next_state = board.next_state(state, action)
        
            if board.is_ended(next_state):
                scores = board.points_values(next_state)

                if scores[player] == 1:
                    state = next_state
                    break
    
        else:
            # Prefer center moves
            center_moves = [a for a in actions if (a[2], a[3]) == (1, 1)]

            if center_moves:
                action = choice(center_moves)
            else:
                # Prefer corner moves
                corner_moves = [
                    a for a in actions
                    if (a[2], a[3]) in [(0, 0), (0, 2), (2, 0), (2, 2)]
                ]

                if corner_moves:
                    action = choice(corner_moves)
                else:
                    action = choice(actions)

            state = board.next_state(state, action)
            
    return state


def backpropagate(node: MCTSNode|None, won: bool):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    while node is not None:
        node.visits += 1

        if won:
            node.wins += 1

        node = node.parent

def ucb(node: MCTSNode, is_opponent: bool):
    """ Calcualtes the UCB value for the given node from the perspective of the bot

    Args:
        node:   A node.
        is_opponent: A boolean indicating whether or not the last action was performed by the MCTS bot
    Returns:
        The value of the UCB function for the given node
    """
    if node.visits == 0:
        return float("inf")
    
    win_rate = node.wins / node.visits

    if is_opponent:
        win_rate = 1 - win_rate
    
    exploration = explore_faction * sqrt(log(node.parent.visits) / node.visits)

    return win_rate + exploration

def get_best_action(root_node: MCTSNode):
    """ Selects the best action from the root node in the MCTS tree

    Args:
        root_node:   The root node
    Returns:
        action: The best action from the root node
    
    """
    best_action = None
    most_visits = float("-inf")

    for action, child in root_node.child_nodes.items():
        if child.visits > most_visits:
            most_visits = child.visits
            best_action = action
    
    return best_action

def is_win(board: Board, state, identity_of_bot: int):
    # checks if state is a win state for identity_of_bot
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state, previous_tree=None):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        current_state:  The current state of the game.
        previous_tree: The previous MCTS tree, if any.

    Returns:    The action to be taken from the current state

    """
    bot_identity = board.current_player(current_state) # 1 or 2
    root_node = previous_tree
    root_node.parent = None
    
    for _ in range(num_nodes):
        state = current_state
        node = root_node

        # Do MCTS - This is all you!
        # ...

        node, state = traverse_nodes(node, board, state, bot_identity)
        node, state = expand_leaf(node, board, state)
        terminal_state = rollout(board, state)
        won = is_win(board, terminal_state, bot_identity)
        backpropagate(node, won)

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_action = get_best_action(root_node)
    
    print(f"Action chosen: {best_action}")
    return best_action
