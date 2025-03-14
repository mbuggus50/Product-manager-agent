from flask import Flask, request
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, origins='*', allow_headers=['Content-Type', 'Authorization', 'Accept'])
    return app
