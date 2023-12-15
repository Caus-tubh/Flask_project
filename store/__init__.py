import os
from store.models import db
from store.API import product_API, inventory_API, user_API
from flask import Flask
from os.path import join, dirname, realpath
from flask_restful import Api
from flask_cors import CORS
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "Mydb.sqlite3"),
        UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/')
    )
    #app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(app.instance_path, "Mydb.sqlite3") 

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    api = Api(app)
    CORS(app)
    with app.app_context():
        from store import auth,browse,manager,cart,stats
        db.create_all()
        app.register_blueprint(auth.bp)
        app.register_blueprint(browse.bp)
        app.register_blueprint(manager.bp)
        app.register_blueprint(cart.bp)
        app.register_blueprint(stats.bp)

        api.add_resource(product_API, '/api/product', 
                         '/api/product/<string:product_name>', 
                         '/api/pet/<string:product_name>/uploadImage',
                         '/api/product/findByCategory','/api/product/<int:product_id>')
        api.add_resource(inventory_API, '/api/inventory', '/api/inventory/<string:category_name>')
        api.add_resource(user_API, '/api/user', '/api/user/login', '/api/user/logout')
    return app

