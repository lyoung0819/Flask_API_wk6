from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


app = Flask(__name__)

#Set config for the app with from_obj
app.config.from_object(Config)

# Create a SQL Alchemy instance called db which will be central obj (passing in 'app', the instance of our flask app)
db = SQLAlchemy(app)

# Create an instance of Migrate

migrate = Migrate(app, db)

from . import routes, models