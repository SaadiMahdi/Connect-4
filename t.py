import numpy as np


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

        # Check for a win diagonally (bottom-left to top-right)
        for row in range(3, self.rows):
            for col in range(self.cols - 3):
                if all(self.board[row - i][col + i] == piece for i in range(4)):
                    return True

        # Check for a win diagonally (top-left to bottom-right)
        for row in range(self.rows - 3):
            for col in range(self.cols - 3):
                if all(self.board[row + i][col + i] == piece for i in range(4)):
                    return True

        return False

    def gameOver(self):
        return self.win(1) or self.win(2) or len(self.getPossibleMoves()) == 0

    def heuristicEval(self, piece):
        score = 0

        score += 10 * self.countConsecutive(piece, 4)  # Four in a row
        score += 5 * self.countConsecutive(piece, 3)  # Three in a row
        score += 3 * self.countConsecutive(piece, 2)  # Two in a row

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

    def heuristicEval5(self, piece):
        if self.win(piece):
            return 10000
        return 0

    def heuristicConsecutivePieces(self, piece):
        score = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == piece:
                    # Check horizontally
                    if col <= self.cols - 4 and self.board[row][col + 3] == piece:
                        score += 1
                    # Check vertically
                    if row <= self.rows - 4 and self.board[row + 3][col] == piece:
                        score += 1
                    # Check diagonally (bottom-left to top-right)
                    if (
                        row >= 3
                        and col <= self.cols - 4
                        and self.board[row - 3][col + 3] == piece
                    ):
                        score += 1
                    # Check diagonally (top-left to bottom-right)
                    if (
                        row <= self.rows - 4
                        and col <= self.cols - 4
                        and self.board[row + 3][col + 3] == piece
                    ):
                        score += 1
        return score

    def heuristicEval4(self, piece):
        own_threats = self.heuristicConsecutivePieces(piece)
        opponent_piece = 1 if piece == 2 else 2
        opponent_threats = self.heuristicConsecutivePieces(opponent_piece)
        return own_threats - opponent_threats


class Play:
    def __init__(self):
        self.board = ConnectFourBoard()

    def humanTurn(self):
        print("human turn!!!")
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
            self.board.makeMove(row, col, 1)

    def computerTurn(self):
        print("computer turn!!!")
        _, move = self.minimaxAlphaBetaPruning(
            self.board, 5, float("-inf"), float("inf"), True
        )
        self.board.makeMove(move[0], move[1], 2)

    def minimaxAlphaBetaPruning(self, board, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or board.gameOver():
            return board.heuristicEval5(2), None

        possible_moves = board.getPossibleMoves()
        # print(possible_moves)

        if maximizingPlayer:
            maxEval = float("-inf")
            bestMove = None
            for col in possible_moves:
                row = max([r for r in range(board.rows) if board.board[r][col] == 0])
                board.makeMove(row, col, 2)
                eval, _ = self.minimaxAlphaBetaPruning(
                    board, depth - 1, alpha, beta, False
                )
                board.makeMove(row, col, 0)
                if eval > maxEval:
                    maxEval = eval
                    bestMove = (row, col)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            # print(bestMove)
            return maxEval, bestMove
        else:
            minEval = float("inf")
            bestMove = None
            for col in possible_moves:
                row = max([r for r in range(board.rows) if board.board[r][col] == 0])
                board.makeMove(row, col, 1)
                eval, _ = self.minimaxAlphaBetaPruning(
                    board, depth - 1, alpha, beta, True
                )
                board.makeMove(row, col, 0)
                if eval < minEval:
                    minEval = eval
                    bestMove = (row, col)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            # print(bestMove)
            return minEval, bestMove


# Example usage:
game = Play()

while not game.board.gameOver():
    game.board.drawBoard()
    game.humanTurn()
    if game.board.gameOver():
        break
    game.board.drawBoard()
    game.computerTurn()

game.board.drawBoard()
if game.board.win(1):
    print("You win!")
elif game.board.win(2):
    print("Computer wins!")
else:
    print("It's a draw!")
