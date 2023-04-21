from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from jinja2.utils import import_string

from instance.config import TestingConfig, DevelopmentConfig, ProductionConfig

# Create a SQLAlchemy database instance
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name='development'):
    # Create an instance of the Flask app
    app = Flask(__name__)

    # Load configuration settings based on the specified environment
    if config_name == 'production':
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize the database connection
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    # Import and register the app's API routes
    for blueprint_name in app.config['BLUEPRINTS']:
        blueprint = import_string(f'app.routes.{blueprint_name}:{blueprint_name}_bp')
        app.register_blueprint(blueprint, url_prefix=("/api/" + blueprint_name))

    # Initialize JWT
    jwt.init_app(app)

    return app


app = create_app("Production")
