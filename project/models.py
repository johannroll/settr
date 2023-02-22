from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    setlists = db.relationship('Setlist')
    emails = db.relationship('Email')
    
class Setlist(db.Model):
    set_id = db.Column(db.Integer, primary_key=True)
    set_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    songs = db.relationship('Song')
    emails = db.relationship('Email')
    
class Song(db.Model):
    song_id = db.Column(db.Integer, primary_key=True, unique=True)
    song_name = db.Column(db.String(1000))
    song_artist = db.Column(db.String(1000))
    song_album = db.Column(db.String(1000))
    song_key = db.Column(db.String(100))
    song_tempo = db.Column(db.String(100))
    song_performance_key = db.Column(db.String(100), default=None)
    song_sig = db.Column(db.String(100))
    song_mode = db.Column(db.String(100))
    song_preview = db.Column(db.String(1000)) 
    songs_id = db.Column(db.Integer, db.ForeignKey('setlist.set_id'))
    position = db.Column(db.Integer, default=None)
    data = db.Column(db.String)
    
class Email(db.Model):
    email_id = db.Column(db.Integer, primary_key=True)
    email_add = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    set_id = db.Column(db.Integer, db.ForeignKey('setlist.set_id'))
    

    
    