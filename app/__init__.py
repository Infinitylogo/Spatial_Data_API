from flask import Flask
from app.db import init_db
from app.routes import api_bp
from app.dashboard import create_dashboard
from config import Config
from quart import Quart

def create_app():
    # app = Flask(__name__)
    app = Quart(__name__)
    app.config.from_object(Config)
    init_db(app)
    
    # Register Blueprint for APIs
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize both Dashboards
    # location_dashboard = create_dashboard(app, 'location')
    # population_dashboard = create_dashboard(app, 'population')
    
    # # Optionally, you can define URLs to access these dashboards
    # app.wsgi_app = location_dashboard.server.wsgi_app
    # app.wsgi_app = population_dashboard.server.wsgi_app

    return app
