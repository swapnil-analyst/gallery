from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(200))