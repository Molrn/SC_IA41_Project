from copy import deepcopy
from board import ColorBoard, SearchBoard
from chess import Board, SQUARES, parse_square, Move
from time import time


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
