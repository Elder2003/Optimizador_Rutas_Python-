import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_super_secreta'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sistema_rutas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False