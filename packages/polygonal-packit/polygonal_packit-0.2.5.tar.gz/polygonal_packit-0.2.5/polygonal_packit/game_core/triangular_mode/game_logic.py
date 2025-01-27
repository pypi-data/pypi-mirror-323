from . import data_conversions as dc
from . import size_modifications as sm
from . import polygon_creation as pc
from .display import print_board
import numpy as np


def is_placement_valid(board, triangle):
    """
    Checks if a triangle can be placed on the board.
    Performs an element-wise logical AND on the NumPy array representations of the board and triangle.
    The result gives the points of intersection between the triangle and the board.
    If the number of intersection points is zero, the placement is valid.

    Args:
        triangle (numpy.ndarray): A NumPy array representation of a triangle.
        board (numpy.ndarray): A NumPy array representation of a triangular board.

    Returns:
        bool: True if triangle can be placed on board, False otherwise.
    """
    assert isinstance(board, np.ndarray) and isinstance(triangle,
                                                        np.ndarray), (f'Invalid data types. board: {type(board)}, '
                                                                      f'triangle: {type(triangle)}')
    assert board.shape == triangle.shape, f'Shapes do not match. board: {board.shape}, triangle: {triangle.shape}'

    return not np.logical_and(
        board, triangle
    ).sum()  # True only if the sum is equal to 0.


def get_possible_placements(board, k, as_list=False):
    """
    Returns all possible placements of k-element polygons on the given board.

    Args:
        board (numpy.ndarray): A NumPy array representation of a triangular board.
        k (int): The number of elements in the polygon to be placed.
        as_list (bool): If true result is list of lists.

    Returns: list[numpy.ndarray]: A list of NumPy array representations for all possible placements of k-element
    polygons on the board.
    """
    assert isinstance(board, np.ndarray), f'Invalid data types. board: {type(board)}'

    # board_matrix = convert_triangle_to_numpy_array(board)
    n = board.shape[0]
    empty_cells_num = n ** 2 - board.sum()
    result = []
    if k > empty_cells_num:
        return result
    for polygon in pc.get_all_solutions(k):
        for expanded_polygon in sm.expand_polygon(*polygon, n):
            expanded_polygon = dc.convert_triangle_to_numpy_array(expanded_polygon)
            if is_placement_valid(board, expanded_polygon):
                if as_list:
                    result.append(expanded_polygon.tolist())
                else:
                    result.append(expanded_polygon)

    return result


def get_possible_moves(board, turn):
    """
    Returns all possible moves on the given board for the specified turn.

    Args:
        board (numpy.ndarray): A NumPy array representation of a triangular board.
        turn (int): The current turn.

    Returns:
        list[numpy.ndarray]: A list of NumPy array representations of all possible moves.
    """
    assert isinstance(board, np.ndarray), f'Invalid data types. board: {type(board)}'

    return get_possible_placements(board, turn) + get_possible_placements(board, turn + 1)


def place_polygon(board, polygon):
    """
    Places the polygon on the board by adding the NumPy array representation of the polygon to the board.

    Args:
        board (numpy.ndarray): A NumPy array representing the current state of the board.
        polygon (numpy.ndarray): A NumPy array representing the polygon to be placed on the board.

    Returns:
        numpy.ndarray: The updated board after the polygon has been placed.
    """
    assert isinstance(board, np.ndarray) and isinstance(polygon,
                                                        np.ndarray), (f'Invalid data types. board: {type(board)}, '
                                                                      f'triangle: {type(polygon)}')
    assert board.shape == polygon.shape, f'Shapes do not match. board: {board.shape}, triangle: {polygon.shape}'

    return board + polygon


def get_board(board_size):
    """
    Creates board of size board_size.

    Args:
        board_size (int): The size of the board.

    Returns:
        numpy.ndarray: A NumPy array representing the initial state of the board.
    """
    return dc.convert_triangle_to_numpy_array(
        pc.get_triangle_matrix(board_size)
    )


def validate_placements(placements, board):
    """
    Validates an array of placements.

    Args:
        placements (numpy.ndarray): A NumPy array of placements of polygons.
        board (numpy.ndarray): A NumPy array representing the current state of the board.

    Returns:
        numpy.ndarray: Binary vector indicating which placement is valid.
    """

    return np.array(
        [is_placement_valid(board, placement) for placement in placements]
    )


def play(board_size):
    """
    Initiates a terminal-based gameplay session for a triangular board game.

    Args:
        board_size (int): The size of the board.

    Returns:
        None
    """
    board = get_board(board_size)
    turn = 1
    moves = get_possible_moves(board, turn)
    while moves:
        moves_dict = {i: move for i, move in enumerate(moves)}
        for i, move in moves_dict.items():
            print(f'Move {i}:')
            print_board(move)
        print('Board: ')
        print_board(board)
        chosen_move = int(input('Choose move number: '))
        board = place_polygon(board, moves_dict[chosen_move])
        turn += 1
        moves = get_possible_moves(board, turn)
        print('Board: ')
        print_board(board)
    print(f'Player {1 + turn % 2} wins after {turn - 1} turns')
    print('Board: ')
    print_board(board)
    return


if __name__ == '__main__':
    play(15)
