from abc import abstractmethod
import math
from io import BytesIO
import cv2 as cv
import numpy as np
from time import time, sleep
from typing import Union
from collections import OrderedDict
import chess
import chess.svg
import chess.pgn
from PIL import Image
from cairosvg import svg2png
from process import SharlyThread, SharlyProcess
from chessboard import SharlyBoardManager
from common import SharlyOperationHandler, SharlyException


class SharlyGameManager(SharlyThread):
    """ This class schedules the position analysis. """

    def __init__(self, board_manager: SharlyBoardManager):
        """
        Constructor.
        :raises: SharlyException
        """
        super().__init__('sharlychess-game', 'Sharly Chess game manager')
        self.__board_manager = board_manager
        self.__piece_colors_analyser = SharlyPieceColorsAnalyser()

    @property
    def fen(self):
        return self.__piece_colors_analyser.last_accepted_board_fen

    def _loop_action(self) -> None:
        color_signature = self.__board_manager.shift_color_signature()
        if color_signature is not None:
            if self.__piece_colors_analyser.analyse_colors(color_signature) is not None:
                self.__board_manager.set_calibration_signature(
                    self.__piece_colors_analyser.last_accepted_board_color_signature)
        else:
            sleep(0.2)


class SharlyAcceptedBoard(chess.Board):
    """ An accepted position of the current game. """

    max_invalid_signatures = 20

    def __init__(self, previous_board: chess.Board = None, moves: [chess.Move] = None):
        """
        Constructor.
        :param previous_board: the previous board, None for the start position
        :param moves: the moves to add to the previous board
        """
        super().__init__()
        if previous_board is not None:
            # add the moves of the previous board
            for move in previous_board.move_stack:
                self.push(move)
        self.__moves: [chess.Move] = []
        self.__moves_san: [str] = []
        if moves is not None:
            # add the new moves
            for move in moves:
                self.__moves.append(move)
                self.__moves_san.append(self.san(move))
                self.push(move)
        self.__color_signature, \
            self.__turn_pieces_number, \
            self.__opponent_pieces_number = \
            SharlyPieceColorsAnalyser.get_board_color_signature_and_piece_numbers(self)
        self.__color_signature_errors: [OrderedDict] = {}

    @property
    def moves(self) -> [chess.Move]:
        return self.__moves

    @property
    def moves_san(self) -> [str]:
        return self.__moves_san

    @property
    def color_signature(self) -> str:
        return self.__color_signature

    @property
    def turn_pieces_number(self) -> int:
        return self.__turn_pieces_number

    @property
    def opponent_pieces_number(self) -> int:
        return self.__opponent_pieces_number

    def get_color_signature_error(self, depth: int, color_signature: str) -> SharlyException:
        error = None
        try:
            error = self.__color_signature_errors[depth][color_signature]
        except IndexError:
            pass
        except KeyError:
            pass
        return error

    def add_color_signature_error(self, depth: int, color_signature: str, exception: SharlyException) -> None:
        if depth not in self.__color_signature_errors:
            self.__color_signature_errors[depth] = OrderedDict()
        if len(self.__color_signature_errors[depth]) >= self.max_invalid_signatures:
            self.__color_signature_errors[depth].popitem(last=False)
        self.__color_signature_errors[depth][color_signature] = exception


class SharlyAbstractPieceColorsAnalyser(SharlyOperationHandler):
    """
    An abstract class for piece colors analysers.
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()

    @abstractmethod
    def analyse_colors(self, target_color_signature: str) -> chess.Board:
        """ Find the moves from the piece colors. """
        raise NotImplemented()


class SharlyPieceColorsAnalyser(SharlyAbstractPieceColorsAnalyser):
    """
    This class analyses the piece colors.
    """

    __empty_fen = '8/8/8/8/8/8/8/8'

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
        self.__accepted_boards: [SharlyAcceptedBoard] = []
        '''
        accepted_board = SharlyAcceptedBoard()
        self.__accepted_boards.append(accepted_board)
        accepted_board = SharlyAcceptedBoard(
            accepted_board,
            moves=[
                chess.Move.from_uci('e2e4'),
                chess.Move.from_uci('e7e5'),
                chess.Move.from_uci('g1f3'),
                chess.Move.from_uci('b8c6'),
            ])
        # self.__accepted_boards.append(accepted_board)
        accepted_board = SharlyAcceptedBoard(
            accepted_board,
            moves=[
                chess.Move.from_uci('d2d4'),
                chess.Move.from_uci('e5d4'),
                chess.Move.from_uci('f1c4'),
            ])
        # self.__accepted_boards.append(accepted_board)
        accepted_board = SharlyAcceptedBoard(
            accepted_board,
            moves=[
                chess.Move.from_uci('f8c5'),
                chess.Move.from_uci('c2c3'),
            ])
        # self.__accepted_boards.append(accepted_board)
        '''
        self.__load_state()
        self.__last_detected_color_signature: str
        self.__last_detected_color_signature = None
        self.__last_info_time: int = 0
        self.__search_depth = 5
        self.__search_time = 2
        self.__log_analysis = False
        self._init_window('analyse_colors', '6. Analyse colors', )

    @classmethod
    def _state_file(cls):
        return SharlyProcess.state_dir + '/game.json'

    def __save_state(self):
        uci_move_sequences: [[str]] = []
        for accepted_board in self.__accepted_boards:
            uci_moves: [str] = []
            for move in accepted_board.moves:
                uci_moves.append(move.uci())
            uci_move_sequences.append(uci_moves)
        self._write_state({
            'uci_move_sequences': uci_move_sequences
        })

    def __load_state(self):
        previous_state = self.state()
        self.__accepted_boards = []
        accepted_board = None
        try:
            for uci_moves in previous_state['uci_move_sequences']:
                if len(uci_moves) == 0:
                    accepted_board = SharlyAcceptedBoard()
                else:
                    moves = []
                    for uci_move in uci_moves:
                        moves.append(chess.Move.from_uci(uci_move))
                    accepted_board = SharlyAcceptedBoard(accepted_board, moves)
                self.__accepted_boards.append(accepted_board)
        except KeyError:  # probably no state before
            pass

    @property
    def __last_accepted_board(self) -> SharlyAcceptedBoard:
        accepted_board = None
        try:
            accepted_board = self.__accepted_boards[-1]
        except IndexError:
            pass
        return accepted_board

    @property
    def last_accepted_board_fen(self) -> str:
        if self.__last_accepted_board is None:
            return self.__empty_fen
        else:
            return self.__last_accepted_board.board_fen()

    @property
    def last_accepted_board_color_signature(self) -> str:
        fen = self.last_accepted_board_fen
        # split the lines, reverse and join (put 8th rank at the end of the signature)
        fen_ranks = fen.split('/')
        color_signature = ''.join(reversed(fen_ranks))
        replacements = {
            'K': 'P', 'Q': 'P', 'R': 'P', 'B': 'P', 'N': 'P',
            'k': 'p', 'q': 'p', 'r': 'p', 'b': 'p', 'n': 'p',
        }
        for i in range(self._chessboard_size):
            replacements['{}'.format(i+1)] = '_' * (i + 1)
        for search, replace in replacements.items():
            color_signature = color_signature.replace(search, replace)
        color_signature = color_signature.replace('P', 'w').replace('p', 'b')
        return color_signature

    @staticmethod
    def get_board_color_signature_and_piece_numbers(board: chess.Board) -> (str, int, int):
        """ Return the color signature, the number of turn pieces, the number of opponent pieces for the board. """
        signature = ''
        w = 0
        b = 0
        for square in chess.SQUARES:
            color = board.color_at(square)
            if color is None:
                signature += '_'
            elif color == chess.WHITE:
                signature += 'w'
                w += 1
            else:
                signature += 'b'
                b += 1
        if board.turn == chess.WHITE:
            return signature, w, b
        else:
            return signature, b, w

    @staticmethod
    def __get_color_signature_piece_numbers(color_signature: str, turn: bool) -> (int, int):
        """
        Return the number of turn pieces and the number of opponent pieces for the given color signature and the turn.
        """
        w = 0
        b = 0
        for c in color_signature:
            if c == 'w':
                w += 1
            elif c == 'b':
                b += 1
        if turn == chess.WHITE:
            return w, b
        else:
            return b, w

    @staticmethod
    def __get_color_signature_clearances(board_color_signature: str, turn: bool, color_signature: str) -> (int, int):
        """
        Return the number of turn and opponent clearances for the given color signature and the original board.
        """
        w = 0
        b = 0
        for square in chess.SQUARES:
            if color_signature[square] == '_':
                if board_color_signature[square] == 'w':
                    w += 1
                elif board_color_signature[square] == 'b':
                    b += 1
        if turn == chess.WHITE:
            return w, b
        else:
            return b, w

    @staticmethod
    def __get_color_signature_fen(color_signature: str) -> str:
        board = chess.Board(fen=SharlyPieceColorsAnalyser.__empty_fen)
        for square in chess.SQUARES:
            color_char = color_signature[square]
            if color_char == 'w':
                board.set_piece_at(square, chess.Piece(chess.PAWN, chess.WHITE))
            elif color_char == 'b':
                board.set_piece_at(square, chess.Piece(chess.PAWN, chess.BLACK))
        return board.board_fen()

    def __search_start_position(self, target_color_signature: str) -> chess.Board:
        """ Search the start position. """
        start_time = time()
        new_board = None
        errors: [str] = []
        highlighted_squares: [int] = []
        start_color_signature = ('w' * 2 * self._chessboard_size) \
            + ('_' * (self._chessboard_size - 4) * self._chessboard_size) + ('b' * 2 * self._chessboard_size)
        move_detected = target_color_signature != self.__last_detected_color_signature
        if move_detected and target_color_signature == start_color_signature:
            new_board = SharlyAcceptedBoard()
            self.__accepted_boards.append(SharlyAcceptedBoard())
            duration = time() - start_time
            self._add_result(duration)
            self._info('Start position found in {:.3f} seconds'.format(duration))
        else:
            for square in chess.SQUARES:
                if start_color_signature[square] != target_color_signature[square]:
                    highlighted_squares.append(square)
            exception = SharlyException(SharlyException.E_BOARD_START_POSITION_NOT_FOUND)
            errors.append(exception.message)
            duration = time() - start_time
            self._add_result(duration, exception.code)
            if start_time - self.__last_info_time > 15:
                self._warning('Start position not found ({:.3f} seconds)'.format(duration))
                self.__last_info_time = start_time
        self.__last_detected_color_signature = target_color_signature
        self.__show(errors, move_detected, highlighted_squares)
        return new_board

    def __get_sorted_candidate_moves(
            self, search_string: str, search_depth: int, previous_moves: [chess.Move], board: chess.Board,
            target_color_signature: str, target_opponent_pieces: int) -> [chess.Move]:
        """ Sort the candidates moves in a manner that most probable moves will be evaluated first. """
        moves_left = search_depth - len(previous_moves)
        turn_moves_left = math.ceil(moves_left / 2)
        board_color_signature, _, board_opponent_pieces = \
            SharlyPieceColorsAnalyser.get_board_color_signature_and_piece_numbers(board)
        turn_captures_needed = board_opponent_pieces - target_opponent_pieces
        turn_clearances_needed, _ = self.__get_color_signature_clearances(
            board_color_signature, board.turn, target_color_signature)
        possible_clearances = turn_moves_left
        if turn_moves_left == 1:
            has_potential_castling_move = False
            for legal_move in board.legal_moves:
                if board.is_castling(legal_move):
                    has_potential_castling_move = True
                    break
        else:
            # notice: it is not enough to check if a legal move is castling right now because castling may be allowed
            # (or disallowed) by intermediary moves
            has_potential_castling_move = board.has_castling_rights(board.turn)
        if has_potential_castling_move:
            possible_clearances += 1  # castling offers one more possible clearance
        if self.__log_analysis:
            self._info('{}: moves_left={}, turn_moves_left={}'.format(search_string, moves_left, turn_moves_left))
            self._info('{}: turn_captures_needed={}, turn_clearances_needed={}, possible_clearances={}'.format(
                search_string, turn_captures_needed, turn_clearances_needed, possible_clearances))
        if turn_clearances_needed > possible_clearances:
            if self.__log_analysis:
                self._info('{}: all moves rejected (too many {} clearances required ({}), only {} possible)'.format(
                    search_string, 'White' if board.turn == chess.WHITE else 'Black', turn_clearances_needed,
                    possible_clearances))
            return []
        ranked_moves = []
        for legal_move in board.legal_moves:
            # give points on the number of captures needed
            if board.is_capture(legal_move):
                if turn_captures_needed == 0:
                    if self.__log_analysis:
                        self._info('{}: move {} rejected (captures not allowed)'.format(
                            search_string, board.san(legal_move)))
                    continue
                capture_score = int(100 * turn_captures_needed / turn_moves_left)
            else:
                if turn_captures_needed == turn_moves_left:
                    if self.__log_analysis:
                        self._info('{}: move {} rejected (only captures allowed)'.format(
                            search_string, board.san(legal_move)))
                    continue
                capture_score = int(100 * (turn_moves_left - turn_captures_needed) / turn_moves_left)
            # give points on the number of clearances needed
            if target_color_signature[legal_move.from_square] != '_':
                if turn_clearances_needed == possible_clearances:
                    if self.__log_analysis:
                        self._info('{}: move {} rejected (only clearances allowed)'.format(
                            search_string, board.san(legal_move)))
                    continue
                clearance_score = int(100 * (possible_clearances - turn_clearances_needed) / possible_clearances)
            else:
                clearance_score = int(100 * turn_clearances_needed / possible_clearances)
            # give points for the to square
            if target_color_signature[legal_move.to_square] == ('w' if board.turn == chess.WHITE else 'b'):
                # max points if the to square gets the target color after the move
                to_score = 100
            elif target_color_signature[legal_move.to_square] == ('b' if board.turn == chess.WHITE else 'w'):
                # less points if the to square gets the wrong color after the move
                to_score = 50
            else:  # target_color_signature[move.to_square] == '_'
                # no points if the to square should be empty on the target
                to_score = 0
            # then give points for the from square
            if target_color_signature[legal_move.from_square] == '_':
                # max points if the from square is empty for the target
                from_score = 100
            elif target_color_signature[legal_move.from_square] == ('b' if board.turn == chess.WHITE else 'w'):
                # less points if the from square should get the opposite color on the target
                from_score = 50
            else:  # target_color_signature[move.from_square] == ('b' if board.turn == chess.WHITE else 'w'):
                # no points if the from square should be unchanged on the target
                from_score = 0
            # eventually give points for piece and castling
            if board.is_castling(legal_move):
                piece_score = 200
            elif board.piece_at(legal_move.from_square).piece_type == chess.PAWN:
                piece_score = 100
            elif board.piece_at(legal_move.from_square).piece_type == chess.BISHOP or \
                    board.piece_at(legal_move.from_square).piece_type == chess.KNIGHT:
                piece_score = 75
            elif board.piece_at(legal_move.from_square).piece_type == chess.ROOK:
                piece_score = 50
            elif board.piece_at(legal_move.from_square).piece_type == chess.QUEEN:
                piece_score = 25
            else:  # board.piece_at(legal_move.from_square).piece_type == chess.KING
                piece_score = 0
            # penalize back moves
            back_score = 100
            for previous_move in previous_moves:
                if previous_move.from_square == legal_move.to_square and \
                        previous_move.to_square == legal_move.from_square:
                    back_score = 0
                    break
            move_score = capture_score + clearance_score + from_score + to_score + piece_score + back_score
            ranked_moves.append({
                'move': legal_move, 'piece': board.piece_at(legal_move.from_square),
                'score': move_score, 'capture_score': capture_score, 'clearance_score': clearance_score,
                'from_score': from_score, 'to_score': to_score, 'piece_score': piece_score, 'back_score': back_score,
            })
        ranked_moves.sort(key=lambda sm: sm['score'], reverse=True)
        sorted_moves = []
        for score_idx in range(len(ranked_moves)):
            ranked_move = ranked_moves[score_idx]
            if self.__log_analysis:
                self._info(
                    '{}: {:>3} {:>5} {:0.2f} (capture={}, clearance={}, from={}, to={}, piece={}, back={})'.format(
                        search_string, score_idx + 1, board.san(ranked_move['move']), ranked_move['score'],
                        ranked_move['capture_score'], ranked_move['clearance_score'], ranked_move['from_score'],
                        ranked_move['to_score'], ranked_move['piece_score'], ranked_move['back_score']))
            sorted_moves.append(ranked_move['move'])
        return sorted_moves

    def __search_moves_from_board(
            self, start_time: float, stop_time: float, search_depth: int, accepted_board_idx: int,
            previous_moves: [chess.Move], previous_moves_san: [str], board: chess.Board, target_color_signature: str,
            target_turn_pieces: int, target_opponent_pieces: int
    ) -> ([chess.Move], [str]):
        """
         Search a legal sequence of moves that leads to the target position from the given board.
        :param start_time:
        :param search_depth:
        :param previous_moves:
        :param previous_moves_san:
        :param board:
        :param target_color_signature:
        :param target_turn_pieces:
        :param target_opponent_pieces:
        :return:
        """
        search_string = 'Search from board #{}'.format(accepted_board_idx)
        if len(previous_moves) > 0:
            search_string += ' after ' + ' '.join(previous_moves_san)
        now = time()
        if now > stop_time:
            msg = '{}: {}'.format(search_string, 'Too much time spent ({:.3f} seconds)'.format(now - start_time))
            if self.__log_analysis:
                self._info(msg)
            raise SharlyException(SharlyException.E_GAME_TIMEOUT, msg)
        # TODO stop if the thread is killed
        sorted_candidate_moves = self.__get_sorted_candidate_moves(
            search_string, search_depth, previous_moves, board,
            target_color_signature, target_opponent_pieces)
        for move in sorted_candidate_moves:
            previous_moves.append(move)
            previous_moves_san.append(board.san(move))
            move_san = board.san(move)
            board.push(move)
            color_signature, w, b = SharlyPieceColorsAnalyser.get_board_color_signature_and_piece_numbers(board)
            if color_signature == target_color_signature:
                if self.__log_analysis:
                    self._info('{}: target position found for move {}'.format(search_string, move_san))
                return previous_moves, previous_moves_san
            if len(previous_moves) < self.__search_depth:
                try:
                    return self.__search_moves_from_board(
                        start_time, stop_time, search_depth, accepted_board_idx, previous_moves, previous_moves_san,
                        board, target_color_signature, target_opponent_pieces, target_turn_pieces)
                except SharlyException as e:
                    if e.code == SharlyException.E_GAME_TIMEOUT:
                        raise e
            else:
                if self.__log_analysis:
                    self._info('{}: target position not found for move {}, maximum depth has been reached'.format(
                        search_string, move_san))
                pass
            previous_moves_san.pop()
            previous_moves.pop()
            board.pop()
        msg = '{}: no legal move sequence matches'.format(search_string)
        if self.__log_analysis:
            self._info(msg)
        raise SharlyException(SharlyException.E_GAME_INVALID_POSITION, msg)

    def __search_moves_with_depth_from_accepted_board(
            self, start_time: float, stop_time: float, search_depth: int, target_color_signature: str,
            accepted_board_idx: int
    ) -> Union[SharlyAcceptedBoard, None]:
        """
        Check that the given position is correct by searching a legal sequence of moves starting from an already
        accepted board.

        :param start_time:
        :param stop_time:
        :param search_depth:
        :param target_color_signature:
        :param accepted_board_idx:
        :return: None if the accepted board matches without any move, or the the new accepted board
        :raises SharlyException: when no move sequence is found
        """
        if self.__log_analysis:
            if accepted_board_idx == len(self.__accepted_boards) - 1:
                self._info('Searching moves from last accepted board (#{}) with depth {}...'.format(
                    accepted_board_idx, search_depth))
            else:
                self._info('Searching moves from previously accepted board #{} with depth {}...'.format(
                    accepted_board_idx, search_depth))
        accepted_board = self.__accepted_boards[accepted_board_idx]
        if target_color_signature == accepted_board.color_signature:
            # nothing changed regarding to a previously accepted board
            # simply return None (all the subsequent boards will be deleted)
            if self.__log_analysis:
                self._info('Signatures match, revert to previously accepted board (#{})\n{}'.format(
                    accepted_board_idx, accepted_board))
            return None
        exception = accepted_board.get_color_signature_error(search_depth, target_color_signature)
        if exception is not None:
            # the signature has already been rejected
            raise SharlyException(SharlyException.E_GAME_ALREADY_REJECTED, message=exception.message, repeated=True)
        try:
            if self.__log_analysis:
                self._info('Board #{} - POSITION: turn={}, turn_pieces={}, opponent_pieces={}, signature={}\n{}'.format(
                    accepted_board_idx, 'White' if accepted_board.turn == chess.WHITE else 'Black',
                    accepted_board.turn_pieces_number, accepted_board.opponent_pieces_number,
                    accepted_board.color_signature, accepted_board))
            # check the number of W/B pieces on the target
            target_turn_pieces_number, target_opponent_pieces_number = \
                self.__get_color_signature_piece_numbers(
                    target_color_signature, accepted_board.turn)
            if self.__log_analysis:
                self._info('Board #{} - TARGET: turn_pieces={}, opponent_pieces={}, signature={}\n{}'.format(
                    accepted_board_idx, target_turn_pieces_number, target_opponent_pieces_number,
                    target_color_signature,
                    str(chess.Board(self.__get_color_signature_fen(
                        target_color_signature))).replace('P', 'o').replace('p', 'x')))
            turn_moves = math.ceil(search_depth / 2)
            opponent_moves = math.floor(search_depth / 2)
            if self.__log_analysis:
                self._info('Board #{} - MOVES: turn={}, opponent={}'.format(
                    accepted_board_idx, turn_moves, opponent_moves))
            if target_turn_pieces_number > accepted_board.turn_pieces_number:
                raise SharlyException(
                    SharlyException.E_GAME_TOO_MANY_PIECES_REQUIRED,
                    'Board #{} - Too many {} pieces required ({}), only {} available'.format(
                        accepted_board_idx, 'White' if accepted_board.turn == chess.WHITE else 'Black',
                        target_turn_pieces_number, accepted_board.turn_pieces_number))
            if target_opponent_pieces_number > accepted_board.opponent_pieces_number:
                raise SharlyException(
                    SharlyException.E_GAME_TOO_MANY_PIECES_REQUIRED,
                    'Board #{} - Too many {} pieces required ({}), only {} available'.format(
                        accepted_board_idx, 'Black' if accepted_board.turn == chess.WHITE else 'White',
                        target_opponent_pieces_number, accepted_board.opponent_pieces_number))
            if target_turn_pieces_number < accepted_board.turn_pieces_number - opponent_moves:
                raise SharlyException(
                    SharlyException.E_GAME_TOO_MANY_CAPTURES_REQUIRED,
                    'Board #{} - Too many {} captures required ({}), only {} possible'.format(
                        accepted_board_idx, 'White' if accepted_board.turn == chess.WHITE else 'Black',
                        accepted_board.turn_pieces_number - target_turn_pieces_number, opponent_moves))
            if target_opponent_pieces_number < accepted_board.opponent_pieces_number - turn_moves:
                raise SharlyException(
                    SharlyException.E_GAME_TOO_MANY_CAPTURES_REQUIRED,
                    'Board #{} - Too many {} captures required ({}), only {} possible'.format(
                        accepted_board_idx, 'Black' if accepted_board.turn == chess.WHITE else 'White',
                        accepted_board.opponent_pieces_number - target_opponent_pieces_number, turn_moves))
            # check the number of clearances
            target_turn_clearances, target_opponent_clearances = self.__get_color_signature_clearances(
                accepted_board.color_signature, accepted_board.turn, target_color_signature)
            if self.__log_analysis:
                self._info('Board #{} - TARGET CLEARANCES: turn={}, opponent={}'.format(
                    accepted_board_idx, target_turn_clearances, target_opponent_clearances))
            possible_turn_clearances = turn_moves \
                + (1 if accepted_board.has_castling_rights(accepted_board.turn) else 0)
            if target_turn_clearances > possible_turn_clearances:
                raise SharlyException(
                    SharlyException.E_GAME_TOO_MANY_CLEARANCES_REQUIRED,
                    'Board #{} - Too many {} clearances required ({}), only {} possible'.format(
                        accepted_board_idx, 'White' if accepted_board.turn == chess.WHITE else 'Black',
                        target_turn_clearances, possible_turn_clearances))
            possible_opponent_clearances = opponent_moves + (1 if accepted_board.has_castling_rights(
                not accepted_board.turn) else 0)
            if target_opponent_clearances > possible_opponent_clearances:
                raise SharlyException(
                    SharlyException.E_GAME_TOO_MANY_CLEARANCES_REQUIRED,
                    'Board #{} - Too many {} clearances required ({}), only {} possible'.format(
                        accepted_board_idx, 'Black' if accepted_board.turn == chess.WHITE else 'White',
                        target_opponent_clearances, possible_opponent_clearances))
            board_start_time = time()
            moves, moves_san = self.__search_moves_from_board(
                start_time, stop_time, search_depth, accepted_board_idx, [], [], accepted_board.copy(),
                target_color_signature, target_turn_pieces_number, target_opponent_pieces_number)
            now = time()
            if self.__log_analysis:
                self._info('Found matching moves in {:.3f} seconds: {}'.format(
                    now - board_start_time, ' '.join(moves_san)))
            return SharlyAcceptedBoard(accepted_board, moves)
        except SharlyException as e:
            if self.__log_analysis:
                self._info(e)
            if e.code != SharlyException.E_GAME_TIMEOUT:
                accepted_board.add_color_signature_error(search_depth, target_color_signature, e)
            raise e

    def __search_moves_with_depth(
            self, start_time: float, stop_time: float, search_depth: int, target_color_signature: str
    ) -> chess.Board:
        """ Check that the given position is correct by searching a legal sequence of moves with the given depth. """
        exception = None
        for accepted_board_idx in range(len(self.__accepted_boards) - 1, -1, -1):
            board_start_time = time()
            try:
                new_accepted_board = self.__search_moves_with_depth_from_accepted_board(
                    start_time, stop_time, search_depth, target_color_signature, accepted_board_idx)
                now = time()
                # remove all the subsequent already (and probably incorrectly) accepted boards
                self.__accepted_boards = self.__accepted_boards[0:accepted_board_idx + 1]
                if new_accepted_board is None:
                    self._info('NEW POSITION Depth={}: reverted to board #{} in {:.3f} seconds'.format(
                        search_depth, accepted_board_idx, now - board_start_time))
                    self._info('PGN: {}\n{}'.format(
                        self.__board_pgn_moves(self.__last_accepted_board), self.__last_accepted_board))
                else:
                    self.__accepted_boards.append(new_accepted_board)
                    self._info(
                        'NEW POSITION Depth={}: found new move sequence for board #{} in {:.3f} seconds: {}'.format(
                            search_depth, accepted_board_idx, now - board_start_time,
                            ' '.join(new_accepted_board.moves_san)))
                    self._info(
                        'PGN: {}\n{}'.format(
                            self.__board_pgn_moves(self.__last_accepted_board), self.__last_accepted_board))
                return self.__last_accepted_board
            except SharlyException as e:
                if e.code == SharlyException.E_GAME_TIMEOUT:
                    raise e
                # if no move sequence is found, the first exception will be raised
                # (corresponding to the last accepted board)
                if exception is None:
                    exception = e
        raise exception

    def __search_moves(self, color_signature: str) -> chess.Board:
        """ Check that the given position is correct by searching a legal sequence of moves. """
        new_board = None
        move_detected_since_last_accepted = self.__last_accepted_board.color_signature != color_signature
        exception = None
        highlighted_squares: [int] = []
        if move_detected_since_last_accepted:
            for square in chess.SQUARES:
                if self.__last_accepted_board.color_signature[square] != color_signature[square]:
                    highlighted_squares.append(square)
            start_time = time()
            stop_time = start_time + self.__search_time
            for search_depth in range(1, self.__search_depth + 1):
                try:
                    new_board = self.__search_moves_with_depth(start_time, stop_time, search_depth, color_signature)
                    # moves has been found, stop searching
                    exception = None
                    break
                except SharlyException as e:
                    if e.code == SharlyException.E_GAME_TIMEOUT:
                        exception = e
                        # time to stop :-)
                        break
                    if exception is None:
                        exception = e
            now = time()
            if exception is not None:
                if not exception.repeated or now - self.__last_info_time > 15:
                    self._info('{} ({:.3f} seconds)'.format(exception.message, now - start_time))
                    self.__last_info_time = now
        else:
            self._debug('Position unchanged regarding to the last accepted board')
        self.__last_detected_color_signature = color_signature
        self.__show(
            [] if exception is None else [exception.message], move_detected_since_last_accepted, highlighted_squares)
        return new_board

    def analyse_colors(self, target_color_signature: str) -> chess.Board:
        """ Find the moves from the piece colors. """
        if self.__last_accepted_board is None:
            new_board = self.__search_start_position(target_color_signature)
        else:
            new_board = self.__search_moves(target_color_signature)
        if new_board is not None:
            self.__save_state()
        return new_board

    @staticmethod
    def __fen2png(
            dim: int, fen: str, lastmove: chess.Move = None, arrows: [chess.svg.Arrow] = None,
            background_color: str = '#0a0c1b', font_color: str = '#ffffff',
            dark_color: str = '#3dbfef', light_color: str = '#ffffff',
            lastmove_dark_color: str = '#fffeb3', lastmove_light_color: str = '#fffeb3',
            green_arrow_color: str = '#0000aaa0', blue_arrow_color: str = '#0000ffa0',
            yellow_arrow_color: str = '#ffff00a0', red_arrow_color: str = '#ff0000a0',
    ) -> np.ndarray:
        """
        Transform a FEN to an image.
        :param fen: the input FEN
        :param dim: the desired dimension
        :return: a PNG image of the board
        """
        if arrows is None:
            arrows = []
        board = chess.Board(fen)
        svg_data = chess.svg.board(board, arrows=arrows, lastmove=lastmove, colors={
            'square light': light_color,
            'square dark': dark_color,
            'square light lastmove': lastmove_light_color,
            'square dark lastmove': lastmove_dark_color,
            'margin': background_color,
            'coord': font_color,
            'arrow green': green_arrow_color,
            'arrow blue': blue_arrow_color,
            'arrow yellow': yellow_arrow_color,
            'arrow red': red_arrow_color,
        })
        png_data = svg2png(bytestring=svg_data, output_width=dim, output_height=dim)
        pil_image = Image.open(BytesIO(png_data))
        png_image = np.array(pil_image.convert('RGB'))[:, :, ::-1].copy()
        return png_image

    @staticmethod
    def __board_pgn_moves(board: chess.Board):
        if board is None:
            return ''
        game = chess.pgn.Game()
        node = game.game()
        for move in board.move_stack:
            node.add_variation(move)
            node = node.next()
        return str(game).split('\n')[-1]

    def __show(self, errors: [str], move_detected: bool, highlighted_squares: [int]) -> None:
        """ Show the results of the color analysis. """
        rows = 2
        columns = 6
        accepted_board_numbers = rows * columns - 1
        display_text_color = (0, 0, 0, )
        board_dim = 300
        h_margin = 10
        v_margin = 10
        t_margin = 50 + 30
        b_margin = 30
        output_width = h_margin + columns * (board_dim + h_margin)
        output_height = t_margin - v_margin + rows * (board_dim + v_margin) + b_margin
        output = np.ones((output_height, output_width, 3), np.uint8) * 255
        height = t_margin
        width = h_margin
        arrows: [chess.svg.Arrow] = []
        for square in highlighted_squares:
            arrows.append(chess.svg.Arrow(square, square, color='red'))
        output[height:height + board_dim, width:width + board_dim] = self.__fen2png(
            board_dim, self.__get_color_signature_fen(self.__last_detected_color_signature), arrows=arrows,
            background_color='#ffffff', font_color='#551F17', dark_color='#A33A2C', light_color='#b9b8a2')
        for i in range(1, min(accepted_board_numbers + 1, len(self.__accepted_boards) + 1)):
            accepted_board_idx = len(self.__accepted_boards) - i
            accepted_board = self.__accepted_boards[accepted_board_idx]
            row = int(i / columns)
            column = i - row * columns
            width = h_margin + column * (board_dim + h_margin)
            height = t_margin + row * (board_dim + v_margin)
            arrows = []
            for move in accepted_board.moves[:-1]:
                arrows.append(chess.svg.Arrow(move.from_square, move.to_square, color='green'))
            if accepted_board.moves:
                arrows.append(chess.svg.Arrow(
                    accepted_board.moves[-1].from_square, accepted_board.moves[-1].to_square, color='blue'))
            lastmove = None
            if len(accepted_board.move_stack):
                lastmove = accepted_board.move_stack[-1]
            output[height:height + board_dim, width:width + board_dim] = self.__fen2png(
                board_dim, accepted_board.board_fen(), lastmove=lastmove, arrows=arrows)
        strings = ['New move detected' if move_detected else 'Unchanged'] if len(errors) == 0 else []
        self._write_text(
            output, strings,
            display_text_color, errors)
        if len(self.__accepted_boards):
            cv.putText(
                output, self.__board_pgn_moves(self.__accepted_boards[-1]), (10, t_margin - 15),
                cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0, ), thickness=2)
        self._show_window('analyse_colors', output)
