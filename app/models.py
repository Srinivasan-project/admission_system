from . import db

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    academic_background = db.Column(db.Text, nullable=False)
    degree_certificate = db.Column(db.String(200), nullable=False)
    id_proof = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='Pending')
