from copy import deepcopy
from board import ColorBoard, SearchBoard
from chess import Board, SQUARES, parse_square, Move
from time import time
import operator

def run_search_path_V2(color : ColorBoard, board : Board):

    l_search_board = []
    count = 0
    status = 0
    b = [board, 0, 0, Move.null(), 3]
    while status == 0 :
        [l_search_board, status] = search_path_V4(color, b[0], b[1], b[4], l_search_board)
        if status == 0:
            b = deepcopy(l_search_board[0])
            #print(b[0],'\n',b[1],b[2],b[3])
            b[0].push(b[3])
            start = b[3].from_square
            end = b[3].to_square
            if (start == parse_square('e1') and board.piece_at(start).piece_type == 6) and abs(end-start) != 2:
                print(b[0],'\n',b[1],b[2],b[3], b[4])
            l_search_board.pop(0)
            count = count + 1

    return [b[0], count, len(l_search_board)]

"""
V4:

Passage en POO : board.SearchBoard
Ajout d'un coeff dynamique pour gérer au mieux chaque situation
Ajout de tous les coups d'une position si aucun ne correspond
"""

def search_path_V4(color : ColorBoard, board : Board, g : int, coeff : int, l_search_board):

    #Get the number of similar squares, the number of pieces on color board and regular board, the indexes of different squares
    [nb_same,b_w_p,b_b_p,c_w_p,c_b_p,\
    w_left_sq,w_arrive_sq,b_left_sq, b_arrive_sq]\
    = color.board_compare_V2(board)
    if nb_same == 64 :
        # Return if the boards are the same
        return [l_search_board, 1]
    else:
        # compare the number of pieces on each board
        # a greater number of pieces on the color board makes it unreachable
        if c_w_p > b_w_p or c_b_p > b_b_p :
            if g == 0:
            #go back to previous moves if it's the first computation of the board
                return [l_search_board, -1]
            else :
            # Dont explore unreachable options
                return [l_search_board, 0]

        is_white_to_play = board.turn
        h = (64 - nb_same)
        # Get all the legal moves
        legal_moves = list(board.legal_moves)

        # Check if the position of the playing color is already perfect
        # If so, add to the list all moves except pound moves
        if is_white_to_play:
            if len(w_left_sq) == 0:
                for move in legal_moves:
                    if board.piece_at(move.from_square).piece_type != 1:
                        l_search_board = \
                        add_to_list_V2(l_search_board, \
                        [board, g, h+g, move, coeff])
                return [l_search_board, 0]
        else:
            if len(b_left_sq) == 0:
                for move in legal_moves:
                    if board.piece_at(move.from_square).piece_type != 1:
                        l_search_board = \
                        add_to_list_V2(l_search_board, \
                        [board, g, h+g, move, coeff])
                return [l_search_board, 0]

        no_move_added = True
        g = g+1
        # go through all legal moves
        for move in legal_moves:
            # compute h value
            [h_sq,coeff2] = compute_h_V2(h, move, is_white_to_play, w_left_sq,\
            w_arrive_sq, b_left_sq, b_arrive_sq, board, coeff)

            # checks if move is useful to explore
            if h_sq <= h:
                l_search_board = \
                add_to_list_V2(l_search_board, \
                [board, g, h_sq+g, move, coeff2])

                if coeff2 != 0:
                    no_move_added = False

        if no_move_added :
            for move in legal_moves:
                [h_sq,coeff2] = compute_h_V2(h, move, is_white_to_play, w_left_sq,\
                w_arrive_sq, b_left_sq, b_arrive_sq, board, coeff)
                if coeff2 != 0:
                    l_search_board = \
                    add_to_list_V2(l_search_board, \
                    [board, g, h+g, move, coeff])

        return [l_search_board, 0]

def add_to_list_V2(l_search_board, nod):
    index = get_index_V2(nod[2], nod[1], l_search_board)
    l_search_board.insert(index, nod)

    #l_search_board.insert(0, nod)
    #l_search_board.sort(key = operator.itemgetter(1,2))
    return l_search_board

def get_index_V2(f:int,g: int, l_search_board : list):
    size = len(l_search_board)
    index = 0
    while index + 1 < size and l_search_board[index][2] < f:
        index = index + 1
    while index + 1 < size and l_search_board[index][2] == f and l_search_board[index][1] < g :
        index = index + 1
    return index


def abstract_compute_h_V2(start, end, left_list, arrive_list, coeff):
    diff = 0

    if start in left_list :
        diff = diff - coeff
    else :
        coeff = 1
        diff = diff + coeff
    if end in arrive_list :
        diff = diff - coeff
    else :
        diff = diff + coeff
    diff = diff + coeff/1000
    return [diff,coeff]

def compute_h_V2(h, move, is_white_to_play, w_left_sq, w_arrive_sq, b_left_sq, b_arrive_sq, board, coeff):
    diff = 0
    start = move.from_square
    end = move.to_square

    if is_white_to_play :

        if (start == parse_square('e1') and board.piece_at(start).piece_type == 6):
            if abs(end-start) == 2:
                if end == parse_square('g1'):
                     [diff2,coeff] = abstract_compute_h_V2(parse_square('h1'),parse_square('f1'),w_left_sq,w_arrive_sq, coeff)
                     diff = diff + diff2
                else :
                    [diff2,coeff] = abstract_compute_h_V2(parse_square('a1'),parse_square('d1'),w_left_sq,w_arrive_sq, coeff)
                    diff = diff + diff2
            else:
                if board.has_castling_rights(is_white_to_play):
                    coeff = 0
        [diff1,coeff] = abstract_compute_h_V2(start,end,w_left_sq,w_arrive_sq, coeff)
        diff = diff + diff1
    else :
        if (start == parse_square('e8') and board.piece_at(start).piece_type == 6):
            if abs(end-start) == 2:
                if end == parse_square('g8'):
                     [diff2,coeff] = abstract_compute_h_V2(parse_square('h8'),parse_square('f8'),w_left_sq,w_arrive_sq, coeff)
                     diff = diff + diff2
                else :
                    [diff2,coeff] = abstract_compute_h_V2(parse_square('a8'),parse_square('d8'),w_left_sq,w_arrive_sq, coeff)
                    diff = diff + diff2
            else:
                if board.has_castling_rights(is_white_to_play):
                    coeff = 0
        [diff1,coeff] = abstract_compute_h_V2(start,end,b_left_sq,b_arrive_sq, coeff)
        diff = diff + diff1

    return [h + diff, coeff]
