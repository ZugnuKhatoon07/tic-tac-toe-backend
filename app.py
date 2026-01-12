# from flask import Flask
# from flask_socketio import SocketIO, join_room, emit
# import random
# import string

# app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*")

# rooms = {}

# def generate_room_code():
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# @socketio.on("createRoom")
# def create_room():
#     room = generate_room_code()
#     rooms[room] = {
#         "board": [""] * 9,
#         "players": [],
#         "turn": "X"
#     }
#     emit("roomCreated", room)

# @socketio.on("joinRoom")
# def join_room_event(room):
#     if room not in rooms:
#         emit("message", "Room not found")
#         return

#     join_room(room)

#     if len(rooms[room]["players"]) >= 2:
#         emit("message", "Room full")
#         return

#     symbol = "X" if len(rooms[room]["players"]) == 0 else "O"
#     rooms[room]["players"].append(symbol)

#     emit("playerAssigned", {
#         "symbol": symbol,
#         "turn": symbol == "X"
#     })

#     emit("boardUpdate", {
#         "board": rooms[room]["board"],
#         "turn": rooms[room]["turn"]
#     }, room=room)

# @socketio.on("move")
# def move(data):
#     room = data["room"]
#     index = data["index"]

#     if room not in rooms:
#         return

#     if rooms[room]["board"][index] != "":
#         return

#     current = rooms[room]["turn"]
#     rooms[room]["board"][index] = current
#     rooms[room]["turn"] = "O" if current == "X" else "X"

#     emit("boardUpdate", {
#         "board": rooms[room]["board"],
#         "turn": rooms[room]["turn"]
#     }, room=room)

# if __name__ == "__main__":
#     socketio.run(app, host="0.0.0.0", port=5000, debug=True)


# from flask import Flask
# from flask_socketio import SocketIO, join_room, emit
# import random, string

# app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*")

# rooms = {}

# WIN_COMBOS = [
#     (0,1,2),(3,4,5),(6,7,8),
#     (0,3,6),(1,4,7),(2,5,8),
#     (0,4,8),(2,4,6)
# ]

# def generate_room_code():
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# def check_winner(board):
#     for combo in WIN_COMBOS:
#         a,b,c = combo
#         if board[a] and board[a] == board[b] == board[c]:
#             return board[a], combo
#     if "" not in board:
#         return "DRAW", []
#     return None, []

# @socketio.on("createRoom")
# def create_room():
#     room = generate_room_code()
#     rooms[room] = {
#         "board": [""] * 9,
#         "players": [],
#         "turn": "X",
#         "gameOver": False
#     }
#     emit("roomCreated", room)

# @socketio.on("joinRoom")
# def join_room_event(room):
#     if room not in rooms:
#         emit("message", "❌ Room not found")
#         return

#     if len(rooms[room]["players"]) >= 2:
#         emit("message", "❌ Room full")
#         return

#     join_room(room)

#     symbol = "X" if len(rooms[room]["players"]) == 0 else "O"
#     rooms[room]["players"].append(symbol)

#     emit("playerAssigned", {
#         "symbol": symbol,
#         "turn": symbol == "X"
#     })

#     emit("boardUpdate", {
#         "board": rooms[room]["board"],
#         "turn": rooms[room]["turn"]
#     }, room=room)

# @socketio.on("move")
# def move(data):
#     room = data["room"]
#     index = data["index"]

#     if room not in rooms:
#         return

#     roomData = rooms[room]

#     if roomData["gameOver"]:
#         return

#     if roomData["board"][index] != "":
#         return

#     current = roomData["turn"]
#     roomData["board"][index] = current
#     roomData["turn"] = "O" if current == "X" else "X"

#     winner, combo = check_winner(roomData["board"])

#     if winner:
#         roomData["gameOver"] = True
#         emit("boardUpdate", {
#             "board": roomData["board"],
#             "turn": roomData["turn"]
#         }, room=room)

#         emit("gameResult", {
#             "winner": winner,
#             "combo": combo
#         }, room=room)
#         return

#     emit("boardUpdate", {
#         "board": roomData["board"],
#         "turn": roomData["turn"]
#     }, room=room)

# @socketio.on("restart")
# def restart(data):
#     room = data["room"]
#     if room not in rooms:
#         return

#     rooms[room]["board"] = [""] * 9
#     rooms[room]["turn"] = "X"
#     rooms[room]["gameOver"] = False

#     emit("boardUpdate", {
#         "board": rooms[room]["board"],
#         "turn": "X"
#     }, room=room)

# if __name__ == "__main__":
#     socketio.run(app, host="0.0.0.0", port=5000)


from flask import Flask, request
from flask_socketio import SocketIO, join_room, emit
import random, string

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

WIN_COMBOS = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]

def generate_room():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def check_winner(board):
    for a,b,c in WIN_COMBOS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], (a,b,c)
    if "" not in board:
        return "DRAW", ()
    return None, ()

# 🟢 CREATE ROOM
@socketio.on("createRoom")
def create_room():
    room = generate_room()
    rooms[room] = {
        "board": [""] * 9,
        "players": {},   # sid -> X/O
        "turn": "X",
        "gameOver": False
    }
    emit("roomCreated", room)

# 🔵 JOIN ROOM
@socketio.on("joinRoom")
def join_room_event(room):
    if room not in rooms:
        emit("message", "Room not found")
        return

    if len(rooms[room]["players"]) >= 2:
        emit("message", "Room full")
        return

    join_room(room)

    symbol = "X" if "X" not in rooms[room]["players"].values() else "O"
    rooms[room]["players"][request.sid] = symbol

    emit("playerAssigned", {
        "symbol": symbol,
        "turn": symbol == rooms[room]["turn"]
    })

    emit("boardUpdate", {
        "board": rooms[room]["board"],
        "turn": rooms[room]["turn"]
    }, room=room)

# 🎮 MOVE (STRICT CHECK)
@socketio.on("move")
def move(data):
    room = data["room"]
    index = data["index"]

    if room not in rooms:
        return

    game = rooms[room]

    if game["gameOver"]:
        return

    # ❌ NOT YOUR TURN
    if game["players"].get(request.sid) != game["turn"]:
        return

    # ❌ CELL ALREADY FILLED
    if game["board"][index] != "":
        return

    game["board"][index] = game["turn"]
    game["turn"] = "O" if game["turn"] == "X" else "X"

    winner, combo = check_winner(game["board"])

    emit("boardUpdate", {
        "board": game["board"],
        "turn": game["turn"]
    }, room=room)

    if winner:
        game["gameOver"] = True
        emit("gameResult", {
            "winner": winner,
            "combo": combo
        }, room=room)

# 🔄 RESTART
@socketio.on("restart")
def restart(data):
    room = data["room"]
    if room not in rooms:
        return

    rooms[room]["board"] = [""] * 9
    rooms[room]["turn"] = "X"
    rooms[room]["gameOver"] = False

    emit("boardUpdate", {
        "board": rooms[room]["board"],
        "turn": "X"
    }, room=room)

# 💬 CHAT
@socketio.on("chat")
def chat(data):
    emit("chat", data, room=data["room"])

# 😆 EMOJI
@socketio.on("emoji")
def emoji(data):
    emit("emoji", data, room=data["room"])

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
