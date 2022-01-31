from chess import Board, SQUARES

# Class representing the final state of the problem
# Board containing only piece colors and not their type
class ColorBoard:

    # A ColorBoard can be initialized from a Board or a fen
    # default initialization is the starting Board
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

# Console display of a ColorBoard
# 'w' for white pieces, 'b' for black pieces, '.' for empty squares
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

    def board_compare_V1(self, board:Board):
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

# Compare the ColorBoard with a Board
# Return following values :
#   - number of pieces for black and white in each board
#   - number of matching squares
#   - List of squares where a piece leaves for black and for white
#   (i.e pieces that are there in the Board but not there in the ColorBoard)
#   - List of squares where a piece arrives for black and for white
#   (i.e pieces that are there in the ColorBoard but not there in the Board)

    def board_compare(self, board:Board):
        nb_same = 0
        b_white_piece = 0
        b_black_piece = 0
        c_white_piece = 0
        c_black_piece = 0
        white_left_sq = []
        black_left_sq = []
        white_arrive_sq = []
        black_arrive_sq = []

        for sq in SQUARES:
                b = board.piece_at(sq)
                c_is_white= self.board[sq]
                if b == None:
                    if c_is_white == None:
                        nb_same = nb_same + 1
                    else :
                        if c_is_white:
                            c_white_piece = c_white_piece + 1
                            white_arrive_sq.append(sq)
                        else:
                            c_black_piece = c_black_piece + 1
                            black_arrive_sq.append(sq)
                else :
                    if b.color :
                        b_white_piece = b_white_piece + 1
                        if c_is_white != None:
                            if c_is_white:
                                c_white_piece = c_white_piece + 1
                                nb_same = nb_same + 1
                            else :
                                white_left_sq.append(sq)
                                black_arrive_sq.append(sq)
                                c_black_piece = c_black_piece + 1
                        else:
                            white_left_sq.append(sq)
                    else :
                        b_black_piece = b_black_piece + 1
                        if c_is_white != None:
                            if c_is_white :
                                c_white_piece = c_white_piece + 1
                                black_left_sq.append(sq)
                                white_arrive_sq.append(sq)
                            else :
                                c_black_piece = c_black_piece + 1
                                nb_same = nb_same + 1
                        else:
                            black_left_sq.append(sq)

        return [nb_same,b_white_piece,b_black_piece,
        c_white_piece,c_black_piece,
        white_left_sq,white_arrive_sq,
        black_left_sq, black_arrive_sq]
