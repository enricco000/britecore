# accounting/config.py

import os

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath("accounting.sqlite")
SECRET_KEY = os.environ.get('SECRET_KEY') or "f4acd54b5f6b54e1bfabec981da922fa"
