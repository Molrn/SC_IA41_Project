import board
import copy
import chess as ch
import time
from copy import deepcopy
from board import ColorBoard
from chess import Board

#def compute_h(board:Board, nb_same:int, move : ch.Move, diff_sq):


def search_path(color : ColorBoard, board : Board, g : int, l_f, l_g, l_moves, l_board):
    [nb_same,c_piece,b_piece,diff_sq] = color.board_compare(board)
    if nb_same == 64 :
        return [l_moves,l_f,[-2],l_board]
    else:
        if c_piece > b_piece :
            if g < 0:
                board.pop()
                return search_path(color, board, g-1)
            else :
                return False
        h = 64 - nb_same
        legal_moves = list(board.legal_moves)
        for move in legal_moves:
            h_sq = h
            if move.from_square in diff_sq :
                h_sq = h_sq - 1
            if move.to_square in diff_sq :
                h_sq = h_sq - 1
            size = len(l_moves)
            if size == 0:
                l_moves.append(move)
                l_f.append(h_sq+g)
                l_g.append(g)
                l_board.append(board)
            else :
                index = 0
                while l_f[index] < h_sq + g and index + 1 < size :
                    index = index + 1
                l_moves.insert(index,move)
                l_f.insert(index, h_sq+g)
                l_g.insert(index, g)
                l_board.insert(index, board)
        return [l_moves,l_f, l_g, l_board]




fen = "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR"
board = Board()
color = ColorBoard(fen)
g = 0
l_f = []
l_h = []
l_g = []
l_moves = []
l_board =[]
h = 0

print()
print("Starting board :")
print(board)
print()
print("Objective :")
color.print()
print()
print("Start program...",end = "")
start = time.time()
count = 0
while g != -1:
    [l_moves,l_f, l_g, l_board] = search_path(color, board, g, l_f, l_g, l_moves, l_board)
    g = deepcopy(l_g[0]) + 1
    if g != -1:
        count = count + 1
        board = deepcopy(l_board[0])
        board.push(l_moves[0])
        #print(board)
        #print(g,l_f[0])
        l_board.pop(0)
        l_f.pop(0)
        l_g.pop(0)
        l_moves.pop(0)
        

end = time.time()
print("Done")
print()
print("Moves :")
for move in board.move_stack:
    print(move)

print()
print("Final Board :")
print(board)
print()
print(f"Runtime of the program is {end - start}")
print(f"Number of nods explored : {count}")
print(f"Number of branches detected : {len(l_moves) + count}")
