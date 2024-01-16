import numpy as np
import random
import copy


class ConnectFourBoard:
    def __init__(self):
        self.rows = 6
        self.cols = 7
        self.board = np.zeros((self.rows, self.cols), dtype=int)

    def drawBoard(self):
        for row in self.board:
            print("|", end=" ")
            for cell in row:
                if cell == 0:
                    print(" ", end=" | ")
                else:
                    print(cell, end=" | ")
            print("\n" + "-" * (self.cols * 4 - 1))

    def get_board(self):
        return self.board.tolist()

    def set_board(self, board):
        self.board = np.array(board)

    def getPossibleMoves(self):
        return [col for col in range(self.cols) if self.board[0][col] == 0]

    def makeMove(self, row, col, piece):
        self.board[row][col] = piece

    def win(self, piece):
        # Check for a win horizontally
        for row in range(self.rows):
            for col in range(self.cols - 3):
                if all(self.board[row][col + i] == piece for i in range(4)):
                    return True

        # Check for a win vertically
        for row in range(self.rows - 3):
            for col in range(self.cols):
                if all(self.board[row + i][col] == piece for i in range(4)):
                    return True

        for row in range(3, self.rows):
            for col in range(self.cols - 3):
                if all(self.board[row - i][col + i] == piece for i in range(4)):
                    return True

        for row in range(self.rows - 3):
            for col in range(self.cols - 3):
                if all(self.board[row + i][col + i] == piece for i in range(4)):
                    return True

        return False

    def gameOver(self):
        return self.win(1) or self.win(2) or len(self.getPossibleMoves()) == 0

    # heuristic 1
    def heuristicEval1(self, piece):
        score = 0

        score += 250 * self.countConsecutive(piece, 4)  # Four in a row
        score += 50 * self.countConsecutive(piece, 3)  # Three in a row
        score += 10 * self.countConsecutive(piece, 2)  # Two in a row
        score += 3 * self.countConsecutive(piece, 1)  # One in a row

        return score

    def countConsecutive(self, piece, consecutive_length):
        count = 0
        # Horizontal
        for row in range(self.rows):
            for col in range(self.cols - consecutive_length + 1):
                if all(
                    self.board[row][col + i] == piece for i in range(consecutive_length)
                ):
                    count += 1

        # Vertical
        for row in range(self.rows - consecutive_length + 1):
            for col in range(self.cols):
                if all(
                    self.board[row + i][col] == piece for i in range(consecutive_length)
                ):
                    count += 1

        # Diagonal (bottom-left to top-right)
        for row in range(consecutive_length - 1, self.rows):
            for col in range(self.cols - consecutive_length + 1):
                if all(
                    self.board[row - i][col + i] == piece
                    for i in range(consecutive_length)
                ):
                    count += 1

        # Diagonal (top-left to bottom-right)
        for row in range(self.rows - consecutive_length + 1):
            for col in range(self.cols - consecutive_length + 1):
                if all(
                    self.board[row + i][col + i] == piece
                    for i in range(consecutive_length)
                ):
                    count += 1

        return count

    # heuristic2
    def heuristicConsecutivePieces(self, piece):
        score = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == piece:
                    if col <= self.cols - 4 and self.board[row][col + 3] == piece:
                        score += 1

                    if row <= self.rows - 4 and self.board[row + 3][col] == piece:
                        score += 1

                    if (
                        row >= 3
                        and col <= self.cols - 4
                        and self.board[row - 3][col + 3] == piece
                    ):
                        score += 1

                    if (
                        row <= self.rows - 4
                        and col <= self.cols - 4
                        and self.board[row + 3][col + 3] == piece
                    ):
                        score += 1
        return score

    def heuristicEval2(self, piece):
        own_threats = 10 * self.heuristicConsecutivePieces(piece)
        opponent_piece = 1 if piece == 2 else 2
        opponent_threats = 20 * self.heuristicConsecutivePieces(opponent_piece)

        return own_threats - opponent_threats

    # heuristic3
    def heuristicEval3(self, piece):
        score = 0
        consecutive_length = 4

        for row in range(self.rows):
            for col in range(self.cols - consecutive_length + 1):
                set_pieces = [
                    self.board[row][col + i] for i in range(consecutive_length)
                ]
                score += self.calculateSetScore(set_pieces, piece)

        for row in range(self.rows - consecutive_length + 1):
            for col in range(self.cols):
                set_pieces = [
                    self.board[row + i][col] for i in range(consecutive_length)
                ]
                score += self.calculateSetScore(set_pieces, piece)

        for row in range(consecutive_length - 1, self.rows):
            for col in range(self.cols - consecutive_length + 1):
                set_pieces = [
                    self.board[row - i][col + i] for i in range(consecutive_length)
                ]
                score += self.calculateSetScore(set_pieces, piece)

        for row in range(self.rows - consecutive_length + 1):
            for col in range(self.cols - consecutive_length + 1):
                set_pieces = [
                    self.board[row + i][col + i] for i in range(consecutive_length)
                ]
                score += self.calculateSetScore(set_pieces, piece)

        return score

    def calculateSetScore(self, set_pieces, piece):
        # Check if the set is occupied only by the specified player
        if all(cell == piece or cell == 0 for cell in set_pieces):
            # Count the number of pieces the player has in the set
            return set_pieces.count(piece)
        else:
            return 0


class Play:
    def __init__(self, mode="human_vs_computer"):
        self.board = ConnectFourBoard()
        self.mode = mode
        self.player1_piece = 1
        self.player2_piece = 2
        self.player1_heuristic = ConnectFourBoard.heuristicEval1
        self.player2_heuristic = ConnectFourBoard.heuristicEval2

    def humanTurn(self):
        print("Human's turn!!!")
        possible_moves = self.board.getPossibleMoves()
        print("Possible moves:", possible_moves)
        col = int(input("Enter your move (column number): "))
        if col not in possible_moves:
            print("Invalid move. Try again.")
            self.humanTurn()
        else:
            row = max(
                [r for r in range(self.board.rows) if self.board.board[r][col] == 0]
            )
            self.board.makeMove(row, col, self.player1_piece)

    def computerTurn(self, player_piece, player_heuristic):
        print("Player's turn!!!")
        _, move = self.minimaxAlphaBetaPruning(
            self.board, 5, float("-inf"), float("inf"), True, player_heuristic
        )
        self.board.makeMove(move[0], move[1], player_piece)

    def minimaxAlphaBetaPruning(
        self, board, depth, alpha, beta, maximizingPlayer, heuristic_function
    ):
        if depth == 0 or board.gameOver():
            return heuristic_function(board, 2), None

        possible_moves = board.getPossibleMoves()

        if maximizingPlayer:
            maxEval = float("-inf")
            bestMove = None
            for col in possible_moves:
                row = max([r for r in range(board.rows) if board.board[r][col] == 0])
                board.makeMove(row, col, 2)
                eval, _ = self.minimaxAlphaBetaPruning(
                    board, depth - 1, alpha, beta, False, heuristic_function
                )
                board.makeMove(row, col, 0)
                if eval > maxEval:
                    maxEval = eval
                    bestMove = (row, col)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval, bestMove
        else:
            minEval = float("inf")
            bestMove = None
            for col in possible_moves:
                row = max([r for r in range(board.rows) if board.board[r][col] == 0])
                board.makeMove(row, col, 1)
                eval, _ = self.minimaxAlphaBetaPruning(
                    board, depth - 1, alpha, beta, True, heuristic_function
                )
                board.makeMove(row, col, 0)
                if eval < minEval:
                    minEval = eval
                    bestMove = (row, col)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval, bestMove
