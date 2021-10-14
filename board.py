import chess
from chess import Board
from chess import SQUARES


class ColorBoard:
    """docstring for ColorBoard."""

    def __init__(self, *args):
        if len(args) == 0:
            self.board = self.board_to_color(Board())
        elif isinstance(args[0],str):
            self.board = self.fen_to_cboard(args[0])
        elif isinstance(args[0],Board):
            self.board = self.board_to_color(args[0])

    def fen_to_cboard(self,fen:str):
        b = Board(fen)
        return self.board_to_color(b)

    def board_to_color(self,board:Board):
        b = []
        for sq in SQUARES:
            piece = board.piece_at(sq)
            if piece :
                b.append(piece.color)
            else :
                b.append(None)
        return b

    def print(self):
        for sq in SQUARES:
            sq2 = (7-sq//8)*8+sq%8
            if self.board[sq2] != None :
                if self.board[sq2]:
                    print('w', end = " ")
                else:
                    print('b', end = " ")
            else : print('.',end = " ")
            if sq%8 == 7: print()

    def board_compare(self, board:Board):
        nb_same = 0
        same = False
        b_piece = 0
        c_piece = 0
        diff_sq = []
        for sq in SQUARES:
                b = board.piece_at(sq)
                c = self.board[sq]
                same = False
                if b == None:
                    if c == None:
                        same = True
                    else :
                        c_piece = c_piece + 1
                else :
                    b_piece = b_piece + 1
                    if  b.color :
                        if c != None:
                            c_piece = c_piece + 1
                            if c :
                                same = True
                    else :
                        if c != None:
                            c_piece = c_piece + 1
                            if c == False :
                                same = True
                if same:
                    nb_same = nb_same + 1
                else:
                    diff_sq.append(sq)
        return [nb_same,c_piece,b_piece,diff_sq]

    def search_path(self, board : Board, g : int):
        [nb_same,c_piece,b_piece,diff_sq] = self.board_compare(board)
        if nb_same == 64 :
            return True
        else:
            if c_piece > b_piece :
                board.pop()
                return search_path(board, g-1)
            h = 64 - nb_same
            legal_moves = list(board.legal_moves)
            sorted_moves = [legal_moves[0], h]
            for moves in legal_moves:
                if move.from_square in diff_sq :
                    h = h - 1
                if move.to_square in diff_sq :
                    h = h - 1
