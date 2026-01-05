from flask import Flask
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

@socketio.on("join")
def join(data):
    room = data["room"]
    join_room(room)

    if room not in rooms:
        rooms[room] = {
            "board": [""] * 9,
            "player": "X"
        }

    emit("update", rooms[room], room=room)

@socketio.on("move")
def move(data):
    room = data["room"]
    i = data["index"]

    if rooms[room]["board"][i] == "":
        rooms[room]["board"][i] = rooms[room]["player"]
        rooms[room]["player"] = "O" if rooms[room]["player"] == "X" else "X"

        emit("update", rooms[room], room=room)

@socketio.on("restart")
def restart(data):
    room = data["room"]
    rooms[room]["board"] = [""] * 9
    rooms[room]["player"] = "X"
    emit("update", rooms[room], room=room)

if __name__ == "__main__":
    socketio.run(app)
