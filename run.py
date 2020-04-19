from code.app import app
from code.config.db import db
from code.config.bcrypt import bcrypt

db.init_app(app)
bcrypt.init_app(app)
