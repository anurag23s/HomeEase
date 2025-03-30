from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

package_service_association = db.Table(
    "package_service",
    db.Column("package_id", db.Integer, db.ForeignKey("package.id"), primary_key=True),
    db.Column("service_id", db.Integer, db.ForeignKey("service.service_id"), primary_key=True),
)

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

    packages = db.relationship("Package", secondary=package_service_association, back_populates="services")


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

class Professional(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id', ondelete="SET NULL"), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    review_id = db.Column(db.Integer, nullable=True)  # Can be linked to a review table later
    experience = db.Column(db.Integer, default=0)
    availability = db.Column(db.Boolean, default=True)
    govt_id = db.Column(db.String(50), unique=True, nullable=False)
    pincode = db.Column(db.String(10), default="800001")  # Store as string to handle leading zeros

    service = db.relationship("Service", backref="professionals")
    documents = db.relationship("ProfessionalDocument", back_populates="professional", cascade="all, delete-orphan")

class ProfessionalDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.pid', ondelete="CASCADE"), nullable=False)
    doc_link = db.Column(db.String(255), nullable=True)

    professional = db.relationship("Professional", back_populates="documents")

class Customer(db.Model):
    __tablename__ = 'customer'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)

    user = db.relationship("User", backref="customer", uselist=False)
    
class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=True, default=None)

    # Relationship with Service
    services = db.relationship("Service", secondary=package_service_association, back_populates="packages")

    def __init__(self, name, description, price, rating=None):
        self.name = name
        self.description = description
        self.price = price
        self.rating = rating

class ServiceRequest(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id', ondelete="CASCADE"), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id', ondelete="SET NULL"), nullable=True)
    service_name = db.Column(db.String(100), nullable=False)
    package_name = db.Column(db.String(100), nullable=True)
    user_remark = db.Column(db.Text, nullable=True)
    pincode = db.Column(db.String(10), nullable=False)  # Handling leading zeros
    request_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Requested")  # Requested, Accepted, Closed
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.pid', ondelete="SET NULL"), nullable=True)

    # Relationships
    service = db.relationship("Service", backref="requests")
    package = db.relationship("Package", backref="requests")
    professional = db.relationship("Professional", backref="assigned_requests")

    def __init__(self, service_id, service_name, pincode, status="Requested", package_id=None, package_name=None, user_remark=None):
        self.service_id = service_id
        self.service_name = service_name
        self.pincode = pincode
        self.status = status
        self.package_id = package_id
        self.package_name = package_name
        self.user_remark = user_remark
