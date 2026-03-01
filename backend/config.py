import os

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trackit.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
