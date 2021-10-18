import chess as ch
from copy import deepcopy
from board import ColorBoard
from chess import Board, SQUARES, parse_square
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
    for move in b.move_stack:
        print(nb,move)
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
            count = count + 1
            board = deepcopy(l_board[0])
            board.push(l_moves[0])
            #print(board)
            print(count,g,l_f[0], len(l_f), l_moves[0])
            #input()
            l_board.pop(0)
            l_f.pop(0)
            l_g.pop(0)
            l_moves.pop(0)
            length = len(l_f)
    return [board, count, len(l_f)]

"""
Version n°1 :

Implémentation d'A* avec :
    h = nombre de cases différentes + 1 si case arrivée/départ appartient aux cases différentes
    arrêt des variantes ayant moins de pièces
    tri par parcours chaque case du tableau
résultats mat du berger :
    temps : 0.07s
    57 noeuds explorés
    1590 branches détectées
problèmes :
    non détection de la tour lors du roque
    temps de calcul hyper long au bout de quelques coups
        --> liste de coups très longue = tri par valeur long

V2 :
exploration des branches uniquement si cases arrivée/ départ du coup sont différentes sur l'objectif
résultats mat du berger :
    temps : 0.04s
    57 noeuds explorés
    178 branches détectées
problème : position d'un côté bonne = exploration uniquement des coups qui vont sur les cases adverses
ex de fen irresolvables : rnbqkb1r/pppppppp/8/8/4n3/8/PPPPPPPP/RNBQKBNR
fen de départ avec cavalier noir en e4 --> force e4 de la part des blancs
"""
def search_path_V1(color : ColorBoard, board : Board, g : int, l_f, l_g, l_moves, l_board):
    #Get the number of similar squares, the number of pieces on color board and regular board, the indexes of different squares
    [nb_same,c_piece,b_piece,diff_sq] = color.board_compare_V1(board)
    if nb_same == 64 :
        # Return if the boards are the same
        return [l_moves,l_f,[-2],l_board]
    else:
        # compare the number of pieces on each board
        # a greater number of pieces on the color board makes it unreachable
        if c_piece > b_piece :
            if g < 0:
            #go back to previous moves if it's the first computation of the board
                board.pop()
                return search_path_V1(color,board,-1,l_f,l_g,l_moves,l_board)
            else :
            # Dont explore unreachable options
                return [l_moves,l_f, l_g, l_board]

        h = 64 - nb_same
        # Get all the legal moves
        legal_moves = list(board.legal_moves)
        # go through all legal moves
        for move in legal_moves:
            # compute h value
            h_sq = h
            if move.from_square in diff_sq :
                h_sq = h_sq - 1
            if move.to_square in diff_sq :
                h_sq = h_sq - 1
            # checks if move is useful to explore
            if h_sq != h: #ajout de la V2
                size = len(l_moves)
                if size == 0:
                    l_moves.append(move)
                    l_f.append(h_sq+g)
                    l_g.append(g)
                    l_board.append(board)
                else :
                    f = h_sq + g
                    # Go through the list to insert move values at the right spot
                    index = get_index(f,l_f,size)

                    # add values at the right spots in each list
                    l_moves.insert(index,move)
                    l_f.insert(index, f)
                    l_g.insert(index, g)
                    l_board.insert(index, board)
        return [l_moves,l_f, l_g, l_board]
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
                return search_path_V2(color,board,0,l_f,l_g,l_moves,l_board)
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

        for move in legal_moves:
            # compute h value
            h_sq = compute_h(h, move, is_white_to_play, w_left_sq,\
             w_arrive_sq, b_left_sq, b_arrive_sq, board)


            # checks if move is useful to explore
            if h_sq < h:
                [l_moves,l_f, l_g, l_board,size] \
                = add_to_lists(l_moves,l_f, l_g, \
                l_board, move, h_sq, g, board, size)

        return [l_moves,l_f, l_g, l_board]


def get_index(f:int,g: int, l_f:list, l_g:list, size : int):
    index = 0
    while l_f[index] < f and index + 1 < size :
        index = index + 1

    while l_f[index] == f and l_g[index] > g and index + 1 < size :
        index = index + 1
        """index = (borne_inf + borne_sup)//2
        if l_f[index] < f:
            borne_inf = index
        else:
            borne_sup = index"""
    return index

def add_to_lists(l_moves,l_f, l_g, l_board, move, h, g, board, size):
    f = h + g
    if size == 0:
        l_moves.append(move)
        l_f.append(f)
        l_g.append(g)
        l_board.append(board)
    else :
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
    if is_white_to_play :
        diff = abstract_compute_h(start,end,w_left_sq,w_arrive_sq)
        if (start == parse_square('e1') and abs(end-start) == 2 \
        and board.piece_at(start).piece_type == 6):
            if end == parse_square('g1'):
                diff = diff + abstract_compute_h(parse_square('h1'),parse_square('f1'),w_left_sq,w_arrive_sq)
            else :
                diff = diff + abstract_compute_h(parse_square('a1'),parse_square('d1'),w_left_sq,w_arrive_sq)

    else :
        diff = abstract_compute_h(start,end,b_left_sq,b_arrive_sq)
        if (start == parse_square('e8') and abs(end-start) == 2 \
        and board.piece_at(start).piece_type == 6):
            if end == parse_square('g8'):
                diff = diff + abstract_compute_h(parse_square('h8'),parse_square('f8'),w_left_sq,w_arrive_sq)
            else :
                diff = diff + abstract_compute_h(parse_square('a8'),parse_square('d8'),w_left_sq,w_arrive_sq)
    return h + diff

def abstract_compute_h(start, end, left_list, arrive_list):
    diff = 0
    if start in left_list :
        diff = diff - 1
    if end in arrive_list :
        diff = diff - 1
    return diff
