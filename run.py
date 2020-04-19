from code1.app import app
from code1.config.db import db
from code1.config.bcrypt import bcrypt

db.init_app(app)
bcrypt.init_app(app)
