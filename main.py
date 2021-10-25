import chess as ch
from copy import deepcopy
from board import ColorBoard
from chess import Board
from path_finder import search_path_V3, test_finder, compute_h
import operator

#fen complete : w KQkq - 1 0
fen_berger = "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR"
init_castle = "rnbqk1nr/pppp1ppp/8/2b1p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 1 0"
fen_castle = "rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQ1RK1"
fen_long = "r2qk2r/2p3pp/bpn2n2/p2pppB1/QbPPP3/2N2NPB/PP3P1P/R3K2R"
fen_tricky = "r1bqkbnr/pp1ppppp/2n5/2p1N3/8/8/PPPPPPPP/RNBQKBR1"
init_tricky_castle = "r1bqkbnr/pp1ppppp/2n5/2p5/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 1 0"
fen_tricky_castle = "r1bqkb1r/p2ppppp/1pn2n2/2p1N3/2B1P3/8/PPPP1PPP/RNBQ1RK1"

color = ColorBoard(fen_berger)
b = Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR")

test_finder("rnbqk1nr/pppp1ppp/8/2b1p3/2B1P3/8/PPPP1PPP/RNBQ1KNR", b)
