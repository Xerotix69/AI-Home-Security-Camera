from flask import Flask
from app.routes import main_routes
from app.auth import auth_routes
from app.video_processing import video_routes
from app.search import search_routes
from stream import start_stream


def create_app():
    start_stream()
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object('config.Config')
    
    # Register blueprints (modular route handlers)
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(video_routes)
    app.register_blueprint(search_routes)
    
    return app