from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)

    register_blueprints(app)

    return app


def register_blueprints(app):
    import web_api_sl.views as views
    app.register_blueprint(views.bp)


from web_api_sl import models