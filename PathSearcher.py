from copy import deepcopy
from ColorBoard import ColorBoard
from chess import Board, SQUARES, parse_square, Move
from time import time
from Heuristic import abstract_compute_h, compute_h, compute_h_color, compute_h_position
import os

def console_test_finder(color_fen:str, board : Board):

    color = ColorBoard(color_fen)
    os.system("cls")
    print("\nStarting board :")
    print(board)
    print("\nObjective :")
    color.print()
    print("\nStart program...")
    start = time()
    [status, b, count, nb_branches] = run_search_path_V2(color, board)
    end = time()
    if status == 1:
        print("Done\n")
        print("Moves :")
        nb = 1
        for move in b.move_stack:
            print(nb, move)
            nb = nb + 1

        print("\nFinal Board :")
        print(b,"\n")
        print(f"Runtime of the program is {end - start}")
        print(f"Number of nods explored : {count}")
        print(f"Number of branches detected : {nb_branches + count}")
    else:
        if board.move_stack:
            os.system("cls")
            print("Unreachable position, backtracking engaged")
            board.pop()
            console_test_finder(color_fen, board)
        else:
            print("Unreachable position, ending program")


def run_search_path_V2(color : ColorBoard, board : Board):

    l_search_board = []
    count = 0
    status = 0
    b = [board, 0, 0, Move.null(), 3]
    while status == 0 :
        [l_search_board, status] = search_path_V4(color, b[0], b[1], b[4], l_search_board)
        if status == 0:
            b = deepcopy(l_search_board[0])
            b[0].push(b[3])
            l_search_board.pop(0)
            count = count + 1
    return [status, b[0], count, len(l_search_board)]


def search_path_V4(color : ColorBoard, board : Board, g : int,
                   coeff : int, l_search_board: list):

    # Get the number of similar squares, the number of pieces on color board and regular board, the indexes of different squares
    compare = color.board_compare(board)
    [nb_same, bwp_nb, bbp_nb, cwp_nb, cbp_nb, w_left_sq,
     w_arrive_sq,b_left_sq, b_arrive_sq] = compare

    if nb_same == 64 :
        # exit if the boards are the same
        return [l_search_board, 1]
    else:
        # compare the number of pieces on each board
        # a greater number of pieces on the color board makes it unreachable
        if cwp_nb > bwp_nb or cbp_nb > bbp_nb :
            if g == 0:
            # go back to previous moves if it's the first computation of the board
                return [l_search_board, -1]
            else :
            # Don't explore unreachable options
                return [l_search_board, 0]

        # Get all the legal moves
        legal_moves = list(board.legal_moves)

        # Compute the heuristic of the initial position
        # the heuritic of every child move will be computed from this basis
        h = compute_h_position(compare)

        # Check if the position of the playing color is already perfect
        # Then, check if other moves with the same depth are in the list
        # If not, add to the list all moves except pound moves

        if (board.turn and len(w_left_sq) == 0) or (not board.turn and len(b_left_sq) == 0):
            same_depth_exists = False
            for nod in l_search_board:
                if nod[1] == g:
                    same_depth_exists = True
            if not same_depth_exists:
                l_search_board = perfect_position_add(l_search_board, board, legal_moves, g, h, coeff)
            return [l_search_board, 0]

        # Boolean checking if white and black pieces were taken
        w_piece_taken = (bwp_nb > cwp_nb)
        b_piece_taken = (bbp_nb > cbp_nb)

        # Increment number of moves
        g = g+1

        # used to check if moves are added to the the list
        no_move_added = True

        # go through all legal moves
        for move in legal_moves:
            # compute h value
            [h_sq,coeff2] = compute_h(
                h, move, compare,
                w_piece_taken, b_piece_taken,
                board, coeff)

            # checks if move is useful to explore
            if h_sq <= h:
                l_search_board = add_to_list_V2(l_search_board, \
                [board, g, h_sq+g, move, coeff2])
                if coeff2 != 0:
                    no_move_added = False

        if no_move_added :
            for move in legal_moves:
                [h_sq,coeff2] = compute_h(
                    h, move, compare,
                    w_piece_taken, b_piece_taken,
                    board, coeff)
                if coeff2 != 0:
                    l_search_board = add_to_list_V2(l_search_board, \
                    [board, g, 0, move, coeff])
        return [l_search_board, 0]

def perfect_position_add(l_search_board: list, board: Board,
                         legal_moves: list, g: int, h: int, coeff: float):
    for move in legal_moves:
        piece = board.piece_at(move.from_square).piece_type
        if piece != 1:
            if piece == 6:
                if not board.has_castling_rights(board.turn):
                    l_search_board = add_to_list_V2(l_search_board,\
                    [board, g, h+2*coeff+g, move, coeff])
            else:
                l_search_board = add_to_list_V2(l_search_board,\
                [board, g, h+g, move, coeff])
    return l_search_board

def add_to_list_V2(l_search_board: list, nod: list):
    f = nod[2]
    g = nod[1]
    index = get_index_V2(nod[2], nod[1], l_search_board)
    l_search_board.insert(index, nod)
    return l_search_board

def get_index_V2(f:int, g: int, l_search_board: list):
    size = len(l_search_board)
    index = 0
    while index < size and l_search_board[index][2] < f:
        index = index + 1
    while index < size and l_search_board[index][2] == f and l_search_board[index][1] < g :
        index = index + 1
    return index

