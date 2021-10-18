import chess as ch
from copy import deepcopy
from board import ColorBoard
from chess import Board
from path_finder import search_path_V3
from path_finder import test_finder

fen = "r2qk2r/2pp1ppp/bpn2n2/p3p1B1/1bB1P3/2NP4/PPP1NPPP/R2Q1RK1"
b = Board()
c = ColorBoard(fen)

#[l_moves,l_f, l_g, l_board] = search_path_V3(c, b, g, l_f, l_g, l_moves, l_board)

test_finder(fen, b)
