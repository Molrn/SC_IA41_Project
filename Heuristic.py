from chess import SQUARES, Board, Move, parse_square

"""Compute the heuristic of a position
initial heuristic for each child node"""
def compute_h_position (compare : list):
    [nb_same, bwp_nb, bbp_nb, cwp_nb, cbp_nb, w_left_sq,
     w_arrive_sq, b_left_sq, b_arrive_sq] = compare

    """ Heuristic = number of different squares + piece difference
    Favor positions with less squares difference and a fewer piece difference"""
    h = (64 - nb_same) + (bbp_nb + bwp_nb) - (cbp_nb + cwp_nb)

    """Check if each color got a piece taken
    Remove 1 if a one of its piece is on an arrive square for the other color
    favor positions in which pieces are already in position for being taken """
    if bwp_nb > cwp_nb:
        diff = False
        for w_piece in w_left_sq:
            if w_piece in b_arrive_sq:
                diff = True
        if diff:
            h -= 1

    if bbp_nb > cbp_nb:
        diff = False
        for b_piece in b_left_sq:
            if b_piece in w_arrive_sq:
                diff = True
        if diff:
            h -= 1

    return h

""" Compute the heuristic difference for a move from its coeff
Checks if the starting square of the move is in the left list
and if the ending square is in the arrive list
remove 'coeff' if so, add coeff otherwise """
def abstract_compute_h(start: SQUARES, end: SQUARES, left_list: [SQUARES],
                          arrive_list: [SQUARES], coeff: float):
    diff = 0
    if start in left_list :
        diff = diff - coeff
    else :
        #coeff = 1
        diff = diff + coeff
    if end in arrive_list :
        diff = diff - coeff
    else :
        diff = diff + coeff
    # favor moves with a greater coeff
    if diff == 0:
        diff = diff - coeff/10
    return [diff,coeff]

# Select the way to compute the heuristic according to the turn of the Board
def compute_h(h: float, move: Move, compare: list,
                 w_piece_taken: bool, b_piece_taken: bool,
                 board: Board, coeff: float):
    [_, _, _, _, _, w_left_sq, w_arrive_sq, b_left_sq, b_arrive_sq] = compare

    if board.turn:
        [diff, coeff] = compute_h_color(move, board, coeff,
                                        w_left_sq, w_arrive_sq, w_piece_taken,
                                        b_left_sq, b_arrive_sq, b_piece_taken)

    else :
        [diff, coeff] = compute_h_color(move, board, coeff,
                                        b_left_sq, b_arrive_sq, b_piece_taken,
                                        w_left_sq, w_arrive_sq, w_piece_taken)

    return [h + diff, coeff]

""" Compute the heuristic for a specific color
castling problem : a castling move is only represented by a king move
solution : add a second heuristic computation for the rook move"""
def compute_h_color(move: Move, board: Board, coeff: float,
                    left_list: [SQUARES], arrive_list: [SQUARES], piece_taken: [SQUARES],
                    op_left_list: [SQUARES], op_arrive_list: [SQUARES], op_piece_taken: [SQUARES]) :
    start_sq = move.from_square
    end_sq = move.to_square
    diff = 0

# castling problem solving
    if board.turn :
        row = '1'
    else :
        row = '8'
    e_square = parse_square("e" + row)
    # castling moves start from the e1 or e8 square a the piece type of the move is a king
    if start_sq == e_square and board.piece_at(start_sq).piece_type == 6:
        a_square = parse_square("a" + row)
        h_square = parse_square("h" + row)
        # a castling move always moves by 2 squares
        if abs(end_sq-start_sq) == 2:
            g_square = parse_square("g" + row)
            # Check the side of the castling (g square = king side, c square = queen side)
            if end_sq == g_square:
                # compute the heuristic of the H rook move (from H to F row)
                f_square = parse_square("f" + row)
                [diff2,coeff] = abstract_compute_h(h_square,f_square,left_list,arrive_list, coeff)
            else :
                # compute the heuristic of the A rook move (from A to D row)
                d_square = parse_square("d" + row)
                [diff2,coeff] = abstract_compute_h(a_square,d_square, left_list,arrive_list, coeff)
            diff = diff + diff2
        else:
            # unfavor king moves when the player still has castling rights
            if board.has_castling_rights(board.turn):
                # Check if one of the towers left its starting square, unfavor it even more if so
                if a_square in left_list or h_square in left_list :
                    coeff = 0
                else:
                    coeff = 0.5

    7# compute the heuristic difference of the move
    [diff1,coeff] = abstract_compute_h(start_sq, end_sq,left_list, arrive_list, coeff)
    diff = diff + diff1

    """ if pieces were taken from the board, favor moves : 
        - taking opponent pieces
        - putting pieces in squares opponent pieces will arrive to
    Coeff used (2.1*normal_coeff) : > 2 to put these moves before perfect moves
    (i.e moves with starting squares in left_list and landing squares in arrive_list) 
    """
    if piece_taken:
        if end_sq in op_arrive_list :
            diff = diff - 2.1*coeff

    if op_piece_taken:
        if end_sq in op_left_list :
            diff = diff - 2.1*coeff

    return [diff, coeff]

