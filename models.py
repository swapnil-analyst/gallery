from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# EVENT TABLE
class Event(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(200))

# IMAGE TABLE
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(20), nullable=False)
    url = db.Column(db.String(500), nullable=False)