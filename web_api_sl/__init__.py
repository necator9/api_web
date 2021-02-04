from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_moment import Moment

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
moment = Moment()


def create_app(config):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)

        db.init_app(app)
        migrate.init_app(app, db)
        bootstrap.init_app(app)
        moment.init_app(app)

        register_blueprints(app)

    return app


def register_blueprints(app):
    from web_api_sl.views import bp as views_bp
    app.register_blueprint(views_bp)
    from web_api_sl.errors import bp as errors_bp
    app.register_blueprint(errors_bp)


from web_api_sl import models