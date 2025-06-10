from flask_socketio import emit, join_room
from flask import request
from . import socketio  # Initialized SocketIO instance
from .models import Message, db, User  # SQLAlchemy models

# Track connected users (optional, for debugging)
connected_users = {}

@socketio.on("connect")
def handle_connect():
    print(f"[Socket Connected] SID: {request.sid}")


@socketio.on("join")
def handle_join(data):
    email = data.get("email")
    if not email:
        emit("error", {"message": "No email provided"})
        return

    # Join user-specific room
    join_room(email)
    connected_users[request.sid] = email
    print(f"[Room Join] {email} joined room (SID: {request.sid})")

    emit("joined", {"message": f"Joined room for {email}"}, room=email)


@socketio.on("send_message")
def handle_send_message(data):
    sender = data.get("sender")
    receiver = data.get("receiver")
    content = data.get("content")
    is_file = data.get("is_file")
    file_id = data.get("file_id")
    filename = data.get("filename")

    print(filename,file_id,is_file)


    if not all([sender, receiver]):
        emit("error", {"message": "Missing sender, receiver, or content"})
        return

    print(f"[Message] {sender} → {receiver}: {content}")

    # Save to DB
    sender_user = User.query.filter_by(email=sender).first()
    receiver_user = User.query.filter_by(email=receiver).first()

    if not sender_user or not receiver_user:
        emit("error", {"message": "Sender or receiver not found"})
        return

    new_msg = Message(
        sender=sender_user,
        receiver=receiver_user,
        content=content,
        is_file=is_file,
        file_id=file_id,
        filename=filename,
    )
    db.session.add(new_msg)
    db.session.commit()
    print(f"[DB Commit] Message saved from {sender} to {receiver}")
    # Send message to both rooms
    emit("receive_message", data, room=receiver)
    emit("receive_message", data, room=sender)


@socketio.on("disconnect")
def handle_disconnect():
    user_email = connected_users.pop(request.sid, None)
    print(f"[Socket Disconnected] SID: {request.sid}, Email: {user_email}")
