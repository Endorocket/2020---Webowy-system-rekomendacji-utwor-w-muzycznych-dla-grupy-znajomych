from app import app
from config.db import db
from config.bcrypt import bcrypt

db.init_app(app)
bcrypt.init_app(app)
