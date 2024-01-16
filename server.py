from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from connect import ConnectFourBoard, Play

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

board = ConnectFourBoard()
play = Play(mode="human_vs_computer")


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("initial_board", {"board": board.get_board()})


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@socketio.on("reset_board")
def handle_reset_board():
    print("Received reset_board event from client")
    global board

    board.resetBoard()

    updated_board = board.get_board()

    emit("update_board", {"board": updated_board, "player": "pla"}, broadcast=True)


def play_ai_turn():
    global board

    _, move = play.minimaxAlphaBetaPruning(
        board,
        depth=5,
        alpha=float("-inf"),
        beta=float("inf"),
        maximizingPlayer=True,
        heuristic_function=ConnectFourBoard.heuristicEval3,
    )

    board.makeMove(move[0], move[1], play.player2_piece)

    print(f"AI made a move in column {move[1]}")
    print(board.get_board())

    game_over = board.gameOver()

    emit(
        "update_board",
        {
            "board": board.get_board(),
            "game_over": game_over,
            "player": "AI",
        },
        broadcast=True,
    )


@socketio.on("take_turn")
def handle_take_turn(data):
    print("Received take_turn event from client")
    column = data["column"]
    piece = data["piece"]

    print(f"Player made a move in column {column}")

    global board

    board.makeMove(
        max([r for r in range(board.rows) if board.board[r][column] == 0]),
        column,
        piece,
    )

    print(board.get_board())

    # Check for a winner after human move
    game_over = board.gameOver()

    # Broadcast the updated board state to all connected clients
    emit(
        "update_board",
        {
            "board": board.get_board(),
            "game_over": game_over,
        },
        broadcast=True,
    )

    # If the game is not over, play AI turn
    if not game_over:
        print("AI is taking its turn")
        play_ai_turn()


def play_ai_vs_ai():
    global board

    while not board.gameOver():
        # Player 1 (AI) makes a move
        _, move = play.minimaxAlphaBetaPruning(
            board,
            depth=5,
            alpha=float("-inf"),
            beta=float("inf"),
            maximizingPlayer=True,
            heuristic_function=ConnectFourBoard.heuristicEval3,
        )

        board.makeMove(move[0], move[1], play.player1_piece)

        print(f"AI 1 made a move in column {move[1]}")
        print(board.get_board())

        game_over = board.gameOver()

        emit(
            "update_board",
            {
                "board": board.get_board(),
                "game_over": game_over,
                "turn": play.player1_piece,
            },
            broadcast=True,
        )

        # If the game is over, break the loop
        if game_over:
            break

        # Player 2 (AI) makes a move
        _, move = play.minimaxAlphaBetaPruning(
            board,
            depth=5,
            alpha=float("-inf"),
            beta=float("inf"),
            maximizingPlayer=True,
            heuristic_function=ConnectFourBoard.heuristicEval2,
        )

        board.makeMove(move[0], move[1], play.player2_piece)

        print(f"AI 2 made a move in column {move[1]}")
        print(board.get_board())

        # Check for a winner after AI 2 move
        game_over = board.gameOver()

        # Broadcast the updated board state to all connected clients
        emit(
            "update_board",
            {
                "board": board.get_board(),
                "game_over": game_over,
                "turn": play.player2_piece,
            },
            broadcast=True,
        )


@socketio.on("ai_vs_ai")
def handle_ai_vs_ai():
    print("Received ai_vs_ai event from client")
    play_ai_vs_ai()


if __name__ == "__main__":
    socketio.run(app, debug=True)
