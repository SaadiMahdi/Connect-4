from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from connect import ConnectFourBoard, Play

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize board and play instances
board = ConnectFourBoard()
play = Play(mode="human_vs_computer")  # You can change the mode as needed


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

    # Broadcast the updated board state to all connected clients
    emit("update_board", {"board": updated_board}, broadcast=True)


def play_ai_turn():
    global board

    # Use Minimax algorithm for AI move
    _, move = play.minimaxAlphaBetaPruning(
        board,
        depth=5,
        alpha=float("-inf"),
        beta=float("inf"),
        maximizingPlayer=True,
        heuristic_function=ConnectFourBoard.heuristicEval1,
    )

    board.makeMove(move[0], move[1], play.player2_piece)

    print(f"AI made a move in column {move[1]}")
    print(board.get_board())

    # Check for a winner after AI move
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


@socketio.on("take_turn")
def handle_take_turn(data):
    print("Received take_turn event from client")
    column = data["column"]
    player = data["player"]
    piece = data["piece"]

    print(f"Player {player} made a move in column {column}")

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
            "turn": player,
        },
        broadcast=True,
    )

    # If the game is not over, play AI turn
    if not game_over:
        print("AI is taking its turn")
        play_ai_turn()


if __name__ == "__main__":
    socketio.run(app, debug=True)
