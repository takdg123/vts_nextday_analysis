from flask import Flask
from backend import config
from sqlalchemy.pool import NullPool
import os

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = config.alchemy_uri()
    #app.config['SQLALCHEMY_BINDS'] = config.bind_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from backend.models import db
    db.init_app(app)

    from backend.views import public
    app.register_blueprint(public)

    #from backend.schema import schema

    # app.add_url_rule(
    #     '/graphql',
    #     view_func=GraphQLView.as_view(
    #         'graphql',
    #         schema=schema,
    #         graphiql=True # for having the GraphiQL interface
    #     )
    # )

    return app
