from random import choice

def think(board, state, tree=None):
    """ Returns a random move. """
    return choice(board.legal_actions(state))
