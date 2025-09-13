import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request

# Tell Flask to look for templates in the same folder as app.py
app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

users = {}

@app.route('/')
def index():
    return render_template('index.html')  # Will now find index.html in same folder

# The rest of your SocketIO code stays the same...
@socketio.on('join')
def handle_join(data):
    username = data['username']
    pfp = data['pfp']
    users[request.sid] = {'username': username, 'pfp': pfp}
    emit('user_joined', {'username': username, 'pfp': pfp}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    username = users[request.sid]['username']
    pfp = users[request.sid]['pfp']
    message = data['message']
    emit('receive_message', {'username': username, 'pfp': pfp, 'message': message}, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    username = users[request.sid]['username']
    emit('user_typing', {'username': username}, broadcast=True, include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        username = users[request.sid]['username']
        emit('user_left', {'username': username}, broadcast=True)
        users.pop(request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
