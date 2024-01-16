from flask import Flask
from t import ConnectFourBoard, Play
from flask_cors import CORS
from flask import jsonify, request
from flask_socketio import SocketIO, send, emit


app = Flask(__name__)
CORS(
    app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}}
)

socketio = SocketIO(app, cors_allowed_origins="*")

# Your existing ConnectFourBoard and Play classes...


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    board = ConnectFourBoard()
    socketio.emit("initial_board", {"board": board.get_board()})


# @app.route("/")
# def home():
#     return "Hello world !!"


# @app.route("/api/get_board")
# def get_board():
#     board = ConnectFourBoard()
#     return jsonify({"board": board.get_board()})


# @app.route("/api/take_turn", methods=["POST"])
# def take_turn():
#     data = request.get_json()
#     board = ConnectFourBoard()
#     board.set_board(data["board"])
#     board.makeMove(col=data["column"])
#     return jsonify({"board": board.get_board()})


# @app.route("/api/computer_move")
# def computer_move():
#     play = Play()
#     move = play.computerTurn()
#     return jsonify({"move": move})


if __name__ == "__main__":
    socketio.run(app, debug=True)
