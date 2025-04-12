from . import db # . means current package (=website)
from flask_login import UserMixin 
from sqlalchemy.sql import func 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    desig = db.Column(db.String(150))
    posts = db.relationship('Post')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    data = db.Column(db.String(10000))
    picture = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
