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

    def resetBoard(self):
        self.board = np.zeros((self.rows, self.cols), dtype=int)

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
        score += 90 * self.countConsecutive(piece, 3)  # Three in a row
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
        opponent_threats = 200 * self.heuristicConsecutivePieces(opponent_piece)

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

    def heuristicEval4(self, piece):
        weights = {
            "center_control": 1.0,
            "mobility": 1.0,
            "block_threats": 1.0,
            "corner_control": 1.0,
            "piece_count": 1.0,
            "connectivity": 1.0,
            "open_columns": 1.0,
            "threat_analysis": 1.0,
        }

        score = 0

        if self.is_early_game():
            weights["center_control"] = 2.0
            weights["open_columns"] = 0.5

        if self.is_late_game():
            weights["connectivity"] = 2
            weights["block_threats"] = 1.5

        score += weights["center_control"] * self.centerControlHeuristic(piece)
        score += weights["mobility"] * self.mobilityHeuristic(piece)
        score += weights["block_threats"] * self.blockThreatsHeuristic(piece)
        score += weights["corner_control"] * self.cornerControlHeuristic(piece)
        score += weights["piece_count"] * self.pieceCountHeuristic(piece)
        score += weights["connectivity"] * self.connectivityHeuristic(piece)
        score += weights["open_columns"] * self.openColumnsHeuristic(piece)
        score += weights["threat_analysis"] * self.threatAnalysisHeuristic(piece)

        return score

    def is_early_game(self):
        # Placeholder logic, adjust based on your understanding of early game conditions
        return np.count_nonzero(self.board) < 8

    def is_late_game(self):
        # Placeholder logic, adjust based on your understanding of late game conditions
        return np.count_nonzero(self.board) > 12

    def centerControlHeuristic(self, piece):
        center_cols = [2, 3, 4]
        center_control = sum(
            1
            for col in center_cols
            for row in range(self.rows)
            if self.board[row][col] == piece
        )
        return center_control

    def mobilityHeuristic(self, piece):
        possible_moves = self.getPossibleMoves()
        return len(possible_moves)

    def blockThreatsHeuristic(self, piece):
        opponent_piece = 1 if piece == 2 else 2
        opponent_threats = self.countConsecutive(opponent_piece, 3)
        return -opponent_threats  # Penalize blocking opponent threats

    def cornerControlHeuristic(self, piece):
        corners = [(0, 0), (0, 6), (5, 0), (5, 6)]
        corner_control = sum(1 for row, col in corners if self.board[row][col] == piece)
        return corner_control

    def pieceCountHeuristic(self, piece):
        player_pieces = np.count_nonzero(self.board == piece)
        return player_pieces

    def connectivityHeuristic(self, piece):
        connected_pieces = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == piece:
                    # Check horizontally, vertically, and diagonally for connected pieces
                    if col + 3 < self.cols and all(
                        self.board[row][col + i] == piece for i in range(4)
                    ):
                        connected_pieces += 1
                    if row + 3 < self.rows and all(
                        self.board[row + i][col] == piece for i in range(4)
                    ):
                        connected_pieces += 1
                    if (
                        row + 3 < self.rows
                        and col + 3 < self.cols
                        and all(self.board[row + i][col + i] == piece for i in range(4))
                    ):
                        connected_pieces += 1
                    if (
                        row - 3 >= 0
                        and col + 3 < self.cols
                        and all(self.board[row - i][col + i] == piece for i in range(4))
                    ):
                        connected_pieces += 1
        return connected_pieces

    def openColumnsHeuristic(self, piece):
        open_columns = sum(1 for col in range(self.cols) if self.board[0][col] == 0)
        return open_columns

    def threatAnalysisHeuristic(self, piece):
        threats = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == 0:
                    # Check if placing a piece at this position creates a threat
                    self.board[row][col] = piece
                    if self.win(piece):
                        threats += 1
                    self.board[row][col] = 0  # Undo the move
        return threats


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

    def play(self):
        while not self.board.gameOver():
            self.board.drawBoard()
            if self.mode == "1":
                print("human_vs_computer")
                self.humanTurn()
                if not self.board.gameOver():
                    self.board.drawBoard()
                    self.computerTurn(self.player2_piece, self.player2_heuristic)
            elif self.mode == "2":
                print("computer_vs_computer")
                self.computerTurn(self.player1_piece, self.player1_heuristic)
                if not self.board.gameOver():
                    self.board.drawBoard()
                    self.computerTurn(self.player2_piece, self.player2_heuristic)

        self.board.drawBoard()
        if self.board.win(self.player1_piece):
            print("Player 1 wins!" if self.mode == "1" else "Computer 1 wins!")
        elif self.board.win(self.player2_piece):
            print("Computer 2 wins!" if self.mode == "1" else "Computer 2 wins!")
        else:
            print("It's a draw!")

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

    # def monteCarlo(self, simulations=1000):
    #     current_player = 2  # Assuming computer plays first
    #     best_score = float("-inf")
    #     best_move = None

    #     for col in self.board.getPossibleMoves():
    #         row = max(
    #             [r for r in range(self.board.rows) if self.board.board[r][col] == 0]
    #         )
    #         self.board.makeMove(row, col, current_player)
    #         total_score = 0

    #         for _ in range(simulations):
    #             temp_board = copy.deepcopy(self.board)  # Make a copy for simulation
    #             total_score += self.simulateRandomGame(temp_board, current_player)

    #         average_score = total_score / simulations

    #         if average_score > best_score:
    #             best_score = average_score
    #             best_move = (row, col)

    #         self.board.makeMove(row, col, 0)  # Undo the move for next iteration

    #     return best_move

    # def simulateRandomGame(self, board, current_player):
    #     while not board.gameOver():
    #         possible_moves = board.getPossibleMoves()
    #         random_move = random.choice(possible_moves)
    #         row = max(
    #             [r for r in range(board.rows) if board.board[r][random_move] == 0]
    #         )
    #         board.makeMove(row, random_move, current_player)
    #         current_player = 3 - current_player  # Switch player (1 to 2, or 2 to 1)
    #     if board.win(2):  # Assuming computer is player 2
    #         return 1  # Computer wins
    #     elif board.win(1):
    #         return -1  # Human wins
    #     else:
    #         return 0  # It's a draw
