import os
from .extentions import app, db, migrate, jwt, ma
from magic_doc.restful_api.common.web_hook import before_request
from magic_doc.restful_api.common.logger import setup_log

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _register_db(flask_app):
    db.init_app(flask_app)
    with app.app_context():
        db.create_all()


def create_app(config):
    """
    Create and configure an instance of the Flask application
    :param config:
    :return:
    """
    app.static_folder = os.path.join(root_dir, "static")
    if config is None:
        config = {}
    app.config.update(config)
    setup_log(config)
    # _register_db(app)
    migrate.init_app(app=app, db=db)
    jwt.init_app(app=app)
    ma.init_app(app=app)
    from .analysis import analysis_blue
    app.register_blueprint(analysis_blue)

    app.before_request(before_request)

    return app
