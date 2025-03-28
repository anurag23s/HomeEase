from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin, Professional, Customer

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Service(db.Model):
    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    total_bookings = db.Column(db.Integer, nullable=True, default=0)
    avg_rating = db.Column(db.Float, nullable=True, default=None)

    serving_pincodes = db.relationship('ServingPincode', back_populates='service', cascade="all, delete-orphan")


    def __init__(self, service_name, price, description=None):
        self.service_name = service_name
        self.price = price
        self.description = description

class ServingPincode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id', ondelete="CASCADE"), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)  # Store as string to handle leading zeros

    # Relationship
    service = db.relationship('Service', back_populates='serving_pincodes')

    def __init__(self, service_id, pincode):
        self.service_id = service_id
        self.pincode = pincode