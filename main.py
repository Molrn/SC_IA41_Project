from chess import Board
from PathSearcher import console_test_finder
import os

#fen complete : w KQkq - 1 0
fen_start = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
fen_spanish = "rnbqk2r/pp1p1ppp/3b1n2/2p5/4Pp2/3P1N2/PPP1B1PP/RNBQK2R"
fen_berger = "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR"
init_castle = "rnbqk1nr/pppp1ppp/8/2b1p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 1 0"
fen_castle = "rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQ1RK1"
fen_long = "r2qk2r/2p3pp/bpn2n2/p2pppB1/QbPPP3/2N2NPB/PP3P1P/R3K2R"
fen_tricky = "r1bqkbnr/pp1ppppp/2n5/2p1N3/8/8/PPPPPPPP/RNBQKBR1"
init_really_tricky_castle = "r1bqkbnr/pp1ppppp/2n5/2p5/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 1 0"
fen_really_tricky_castle = "r1bqkb1r/p2ppppp/1pn2n2/2p1N3/2B1P3/8/PPPP1PPP/RNBQ1RK1"
init_not_castle = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 0"
fen_not_castle = "rnbqk1nr/pppp1ppp/8/2b1p3/2B1P3/8/PPPP1PPP/RNBQ1KNR"
init_tricky_castle = "rnbqkbnr/pppppppp/8/1B6/2P5/4P3/PP1P1PPP/RNBQK1NR w KQkq - 1 0"
fen_tricky_castle = "r1bqkb1r/pppppppp/2n2n2/1B2N3/2P5/4P3/PP1P1PPP/RNBQ1RK1"
init_yannis = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 1"
fen_yannis = "rnbqk2r/pppp1ppp/5n2/2b1p3/4P3/5Q2/PPPP1PPP/RNB1KBNR w KQkq - 0 1"
fen_perfect = "r1bqkbnr/pppp1ppp/2n5/4p3/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 3"

a = -1
while a != 0:
    while a not in range(0,12):
        os.system("cls")
        print("Choisissez le problème que vous souhaitez résoudre")
        print("1.Mat du berger")
        print("2.Roque 1")
        print("3.Roque 2")
        print("4.Roque 3 (pas résolu)")
        print("5.Long")
        print("6.Remplacement et double déplacement")
        print("7.Remplacement roi-fou")
        print("8.Prise de pièce")
        print("9.Triangulation")
        print("10.Position parfaite")
        print("11.Personnalisé")
        print("0.Quitter")
        print()
        a = int(input())

    init = ""
    end = ""

    if a == 1:
        init = fen_start
        end = fen_berger
    elif a == 2:
        init = init_castle
        end = fen_castle
    elif a == 3:
        init = init_tricky_castle
        end = fen_tricky_castle
    elif a == 4:
        init = init_really_tricky_castle
        end = fen_really_tricky_castle
    elif a == 5:
        init = fen_start
        end = fen_long
    elif a == 6:
        init = fen_start
        end = fen_tricky
    elif a == 7:
        init = init_not_castle
        end = fen_not_castle
    elif a == 8:
        init = fen_start
        end = fen_spanish
    elif a == 9:
        init = init_yannis
        end = fen_yannis
    elif a == 10:
        init = fen_start
        end = fen_perfect
    elif a == 11:
        init = input("Position initiale(fen): ")
        end = input("Position finale(fen): ")
        Board(end)

    if a != 0:
        console_test_finder(end, Board(init))
        print()
        a = -1
        input("Press enter to continue")
