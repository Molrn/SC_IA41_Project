from copy import deepcopy
from board import ColorBoard, SearchBoard
from chess import Board, SQUARES, parse_square, Move
from time import time


def test_finder(color_fen:str, board : Board):

    color = ColorBoard(color_fen)
    print("\nStarting board :")
    print(board)
    print("\nObjective :")
    color.print()
    print("\nStart program...")
    start = time()
    [b, count, nb_branches] = run_search_path_V1(color, board)
    end = time()
    print("Done\n")
    print("Moves :")
    nb = 1
    b2 = board
    coeff = 3
    for move in b.move_stack:
        b2.push(move)
        [nb_same,b_w_p,b_b_p,c_w_p,c_b_p,\
        w_left_sq,w_arrive_sq,b_left_sq, b_arrive_sq]\
        = color.board_compare_V2(b2)
        h_sq = compute_h((64-nb_same), move, b2.turn, w_left_sq,\
        w_arrive_sq, b_left_sq, b_arrive_sq, b2)
        print(nb, move, h_sq + (nb - 1), coeff)
        nb = nb + 1

    print("\nFinal Board :")
    print(b,"\n")
    print(f"Runtime of the program is {end - start}")
    print(f"Number of nods explored : {count}")
    print(f"Number of branches detected : {nb_branches + count}")

def run_search_path_V1(color : ColorBoard, board : Board):
    g = 0
    l_f = []
    l_h = []
    l_g = []
    l_moves = []
    l_board =[]
    h = 0
    count = 0

    while g != -1:
        [l_moves,l_f, l_g, l_board] = search_path_V3(color, board, g, l_f, l_g, l_moves, l_board)
        g = l_g[0] + 1
        if g != -1:
            """if real_move2 in l_moves :
                j = l_moves.index(real_move2)
                for i in range(j) :
                    print(l_board[i], '\n', l_moves[i], l_g[i], l_f[i], len(l_f), i)
                input()"""
            count = count + 1
            board = deepcopy(l_board[0])
            board.push(l_moves[0])
            #print(l_moves[0], g, l_f[0],len(l_f))
            #input()
            l_board.pop(0)
            l_f.pop(0)
            l_g.pop(0)
            l_moves.pop(0)

    return [board, count, len(l_f)]

"""
V3 :

Implémentation d'A* avec :
    h = nombre de cases différentes + 1 si case arrivée/départ appartient aux cases différentes de la couleur
    arrêt des variantes ayant moins de pièces
    bubble sort
    exploration des branches uniquement si cases arrivée/ départ du coup sont différentes sur l'objectif

résolution des problèmes précédents :
    tour roque --> ajout d'un coup de tour quand roque
    coups blancs vers pieces noires alors que position blanche parfaite :
        changement de la fonction ColorBoard.board_compare
            --> retourne valeurs séparées blancs/noirs
            --> Sépare arrivées / départs

Résultats :
    Ultra performant sur positions ou chaque pièce trouve une nouvelle case
        --> mais galère dés qu'une pièce est remplacée par une autre
    Split en fonctions pour les optimiser individuellement
    mat du berger :
        time : 0,02s, nods 34, branches 126
    best result : r2qk2r/2p3pp/bpn2n2/p2pppB1/QbPPP3/2N2NPB/PP3P1P/R3K2R
    profondeur 21, time 0.21s, nods 293, 1645 branches

"""
def search_path_V3(color : ColorBoard, board : Board, g : int, l_f, l_g, l_moves, l_board):
    #Get the number of similar squares, the number of pieces on color board and regular board, the indexes of different squares
    [nb_same,b_w_p,b_b_p,c_w_p,c_b_p,\
    w_left_sq,w_arrive_sq,b_left_sq, b_arrive_sq]\
    = color.board_compare_V2(board)
    if nb_same == 64 :
        # Return if the boards are the same
        return [l_moves,l_f,[-2],l_board]
    else:
        # compare the number of pieces on each board
        # a greater number of pieces on the color board makes it unreachable
        if c_w_p > b_w_p or c_b_p > b_b_p :
            if g == 0:
            #go back to previous moves if it's the first computation of the board
                board.pop()
                return search_path_V3(color,board,0,l_f,l_g,l_moves,l_board)
            else :
            # Dont explore unreachable options
                return [l_moves,l_f, l_g, l_board]

        is_white_to_play = board.turn

        size = len(l_moves)
        h = 64 - nb_same
        # Get all the legal moves
        legal_moves = list(board.legal_moves)
        # go through all legal moves
        if is_white_to_play:
            if len(w_left_sq) == 0:
                for move in legal_moves:
                    if board.piece_at(move.from_square).piece_type != 1:
                        [l_moves,l_f, l_g, l_board,size] \
                        = add_to_lists(l_moves,l_f, l_g, \
                        l_board, move, h, g, board, size)
                return [l_moves,l_f, l_g, l_board]
        else:
            if len(b_left_sq) == 0:
                for move in legal_moves:
                    if board.piece_at(move.from_square).piece_type != 1:
                        [l_moves,l_f, l_g, l_board,size] \
                        = add_to_lists(l_moves,l_f, l_g, \
                        l_board, move, h, g, board, size)
                return [l_moves,l_f, l_g, l_board]
        no_move_added = True
        for move in legal_moves:
            # compute h value
            h_sq = compute_h(h, move, is_white_to_play, w_left_sq,\
            w_arrive_sq, b_left_sq, b_arrive_sq, board)

            # checks if move is useful to explore
            if h_sq <= h:
                [l_moves,l_f, l_g, l_board,size] \
                = add_to_lists(l_moves,l_f, l_g, \
                l_board, move, h_sq, g, board, size)
                no_move_added = False
        if no_move_added :
            for move in legal_moves:
                [l_moves,l_f, l_g, l_board,size] \
                = add_to_lists(l_moves,l_f, l_g, \
                l_board, move, h, g, board, size)
        return [l_moves,l_f, l_g, l_board]

def get_index(f:int,g: int, l_f:list, l_g:list, size : int):
    if f in l_f :
        index = l_f.index(f)
        while l_f[index] == f and l_g[index] > g and index + 1 < size :
            index = index + 1
    else:
        index = 0
        while index + 1 < size and l_f[index] < f :
            index = index + 1

        """index = (borne_inf + borne_sup)//2
        if l_f[index] < f:
            borne_inf = index
        else:
            borne_sup = index"""
    return index

def add_to_lists(l_moves,l_f, l_g, l_board, move, h, g, board, size):
    f = h + g
    # Go through the list to insert move values at the right spot
    index = get_index(f, g, l_f, l_g, size)
    # add values at the right spots in each list
    l_moves.insert(index,move)
    l_f.insert(index, f)
    l_g.insert(index, g)
    l_board.insert(index, board)
    size = size + 1
    return [l_moves,l_f, l_g, l_board,size]

def compute_h(h, move, is_white_to_play, w_left_sq, w_arrive_sq, b_left_sq, b_arrive_sq, board):
    diff = 0
    start = move.from_square
    end = move.to_square
    coeff = compute_coeff(board.move_stack, w_arrive_sq, b_arrive_sq, board.turn)
    if is_white_to_play :
        if (start == parse_square('e1') and board.piece_at(start).piece_type == 6):
            if abs(end-start) == 2 :
                coeff = coeff + 0.5
                if end == parse_square('g1'):
                    diff = diff + abstract_compute_h(parse_square('h1'),parse_square('f1'),w_left_sq,w_arrive_sq, coeff)
                else :
                    diff = diff + abstract_compute_h(parse_square('a1'),parse_square('d1'),w_left_sq,w_arrive_sq, coeff)
            else :
                if board.has_castling_rights(is_white_to_play):
                    coeff = 0
        diff = diff + abstract_compute_h(start,end,w_left_sq,w_arrive_sq, coeff)
    else :
        if (start == parse_square('e8') and board.piece_at(start).piece_type == 6):
            if abs(end-start) == 2 :
                if end == parse_square('g8'):
                    diff = diff + abstract_compute_h(parse_square('h8'),parse_square('f8'),w_left_sq,w_arrive_sq, coeff)
                else :
                    diff = diff + abstract_compute_h(parse_square('a8'),parse_square('d8'),w_left_sq,w_arrive_sq, coeff)
            else:
                if board.has_castling_rights(is_white_to_play):
                    coeff = 0
        diff = diff + abstract_compute_h(start,end,b_left_sq,b_arrive_sq, coeff)
    return h + diff

def compute_coeff(move_stack, w_arrive_sq, b_arrive_sq, turn):
    coeff = 3
    for move in move_stack:
        if turn:
            if move.from_square in b_arrive_sq :
                coeff = 1
            turn = False
        else:
            if move.from_square in w_arrive_sq :
                coeff = 1
            turn = True
    return coeff
"""
différentes solutions :
    1) enlever 1 si cases départ vide et si case arrivée pleine
    2) (1) + ajouter 1 si case départ pleine et si case arrivée vide
    3) modifier le coefficient de différence de (2)
2) avec h_sq < h : parfait pour solutions une pièce / un coup, useless sinon
    - plus précis avec
3) Coefficient haut (3) : met en avant les coups parfaits (part d'une case vide dans color et arrive dans une case pleine)
    mais galère avec coups qui passent par cases identiques
exemples :
    calcule parfaitement r2qk2r/2p3pp/bpn2n2/p2pppB1/QbPPP3/2N2NPB/PP3P1P/R3K2R
        --> shortest move list, perfect piece positioning, time 0.13, 88 nods, 818 branches
    Ne trouve pas le roque simple
Solution envisagé : coefficient dynamique, dépendant de si un pièce jouée est sensée avoir une pièce sur sa case de départ

"""
def abstract_compute_h(start, end, left_list, arrive_list, coeff):
    diff = 0
    if start in left_list :
        diff = diff - coeff
    else :
        diff = diff + coeff
    if end in arrive_list :
        diff = diff - coeff
    else :
        diff = diff + coeff
    diff = diff - coeff/1000
    return diff
