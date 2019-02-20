# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Initialize the application.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'f4acd54b5f6b54e1bfabec981da922fa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounting.sqlite'
db = SQLAlchemy(app)


# Import the views file for routing.
from accounting import views
