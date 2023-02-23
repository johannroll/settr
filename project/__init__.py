import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
# from dotenv import load_dotenv
# load_dotenv()

db = SQLAlchemy()

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'qwerty qwerty'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ylpztkaulixnng:85c565a29e6a5a8bd8c5429e2e7a708924aadbf29cf15db5c2ce6a1cd65ac665@ec2-54-158-247-210.compute-1.amazonaws.com:5432/d1s0drjdu1pq4a'
    # \
    #     'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    from .auth import auth     
    from .main import main 
    
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(main, rl_prefix='/')
    
    from .models import User
    
    create_database(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

def create_database(app):
    if not path.exists('project/' + 'database.db'):
        with app.app_context():
            db.create_all()
            print('Created Database!')

    

   

   