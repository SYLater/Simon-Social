from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS

from website import create_app

app = create_app()
CORS(app)

if __name__ == '__main__':
    app.run( debug=True)
