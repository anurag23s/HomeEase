from flask import Blueprint, request, jsonify, session
from models import db, User, Service,  ServingPincode, Customer, Professional, ServiceRequest, Package, package_service_association
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash 

# Define blueprints first
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)
# Define the service blueprint
service_bp = Blueprint('service', __name__)
CORS(service_bp, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


# Now apply CORS after defining blueprints
CORS(auth_bp, supports_credentials=True)
CORS(admin_bp, supports_credentials=True)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session.permanent = True 
        session['user_id'] = user.id
        session['role'] = user.role
        #session.modified = True  # Ensure session updates

        print("✅ Session after login:", dict(session))  # Debugging session storage

        if user.role == 'admin':
            return jsonify({'redirect': '/admin_dashboard'}), 200
        elif user.role == 'Professional':
            return jsonify({'redirect': '/professional_dashboard'}), 200
        elif user.role == 'Customer':
            return jsonify({'redirect': '/customer_dashboard'}), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@admin_bp.route('/api/add_service', methods=['POST'])
def add_service():
    print("Session Data at add_service:", dict(session))  # 🔍 Debugging session

    if 'role' not in session or session['role'] != 'admin':
        print("❌ Unauthorized - session missing:", dict(session))  # Debugging unauthorized issue
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    service_name = data.get('service_name')
    price = data.get('price')
    description = data.get('description')

    if not service_name or not price:
        return jsonify({'error': 'Service name and price are required'}), 400

    new_service = Service(service_name=service_name, price=price, description=description)
    db.session.add(new_service)
    db.session.commit()

    return jsonify({'message': 'Service added successfully!'}), 201



@auth_bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    role = session.get('role')
    return jsonify({'role': role}), 200

@admin_bp.route("/services", methods=["GET"])
def get_services():
    '''if 'role' not in session or session['role'] != 'admin':
        print("❌ Unauthorized - session missing:", dict(session))  # Debugging unauthorized issue
        return jsonify({'error': 'Unauthorized'}), 403
    '''
    services = Service.query.all()
    service_list = [
        {
            "service_id": service.service_id,
            "service_name": service.service_name,
            "price": service.price,
            "description": service.description,
        }
        for service in services
    ]
    return jsonify(service_list), 200

@admin_bp.route("/add_pincode", methods=["POST"])
def add_pincode():
    data = request.get_json()
    service_id = data.get("service_id")
    pincode = data.get("pincode")

    if not service_id or not pincode:
        return jsonify({"error": "Missing service_id or pincode"}), 400

    new_pincode = ServingPincode(service_id=service_id, pincode=pincode)
    db.session.add(new_pincode)
    db.session.commit()

    return jsonify({"message": "Pincode added successfully"}), 201

@auth_bp.route('/register/customer', methods=['POST'])  # ✅ Change from @app.route to @auth_bp.route
def register_customer():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")
    email = data.get("email")
    contact = data.get("contact")
    address = data.get("address")
    pincode = data.get("pincode")

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400

    if Customer.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)

    try:
        new_user = User(username=username, password_hash=hashed_password, role="Customer")
        db.session.add(new_user)
        db.session.commit()

        new_customer = Customer(
            id=new_user.id,
            full_name=full_name,
            email=email,
            contact=contact,
            address=address,
            pincode=pincode
        )
        db.session.add(new_customer)
        db.session.commit()

        return jsonify({"success": True, "message": "Customer registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    session.pop('role', None)  # Remove role from session
    session.clear()  # Completely clear session (optional)
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route('/api/customer', methods=['GET'])
def get_customer_details():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    customer = Customer.query.filter_by(id=session['user_id']).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    return jsonify({'full_name': customer.full_name}), 200

@auth_bp.route('/api/services', methods=['GET'])
def get_services_for_customer():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    customer = Customer.query.filter_by(id=session['user_id']).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    # Fetch services available in the customer's pincode
    services = db.session.query(Service).join(ServingPincode).filter(ServingPincode.pincode == customer.pincode).all()

    service_list = [
        {
            "service_id": service.service_id,
            "service_name": service.service_name,
            "price": service.price
        }
        for service in services
    ]
    return jsonify(service_list), 200

@auth_bp.route('/api/service-history', methods=['GET'])
def get_service_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Mocking service history (replace with actual service history model if available)
    service_history = [
        {"id": 1, "service_name": "Plumbing Repair", "date": "2025-03-25"},
        {"id": 2, "service_name": "Home Cleaning", "date": "2025-03-22"}
    ]

    return jsonify(service_history), 200


@service_bp.route("/<int:service_id>", methods=["GET"])
def get_service_details(service_id):
    customer_pin = request.args.get("pincode")  # Get customer's pin code from query params

    service = Service.query.get(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404

    # Fetching all packages related to this service
    packages = [
        {
            "id": pkg.id,
            "name": pkg.name,
            "description": pkg.description,
            "price": pkg.price,
        }
        for pkg in service.packages  # Assuming a relationship exists in models.py
    ]

    service_data = {
        "service_id": service.service_id,
        "service_name": service.service_name,
        "price": service.price,
        "description": service.description,
        "avg_rating": service.avg_rating if hasattr(service, "avg_rating") else "N/A",
        "total_bookings": service.total_bookings if hasattr(service, "total_bookings") else 0,
        "is_available": ServingPincode.query.filter_by(service_id=service_id, pincode=customer_pin).first() is not None,
    }

    return jsonify({"service": service_data, "packages": packages})

from flask_cors import cross_origin

@auth_bp.route('/api/book_service', methods=['POST', 'OPTIONS'])
@cross_origin(origin="http://localhost:8081", supports_credentials=True)
def book_service():
    if request.method == "OPTIONS":
        return '', 200  # Handle preflight request

    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    service_id = data.get("service_id")
    service_name = data.get("service_name")
    package_id = data.get("package_id")
    package_name = data.get("package_name")
    user_remark = data.get("user_remark")

    customer = Customer.query.filter_by(id=session['user_id']).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    new_request = ServiceRequest(
        service_id=service_id,
        service_name=service_name,
        pincode=customer.pincode,
        package_id=package_id,
        package_name=package_name,
        user_remark=user_remark
    )

    db.session.add(new_request)
    db.session.commit()

    return jsonify({"message": "Service request created successfully", "request_id": new_request.request_id}), 201

#service_bp = Blueprint("service_bp", __name__)
"""
@auth_bp.route('/api/book_package', methods=['POST', 'OPTIONS'])
@cross_origin(origin="http://localhost:8081", supports_credentials=True)
def book_package():
    if request.method == "OPTIONS":
        return '', 200  # Handle preflight request

    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    package_id = data.get("package_id")
    package_name = data.get("package_name")
    user_remark = data.get("user_remark")

    # Fetch the associated service_id for the given package_id
    package = Package.query.get(package_id)
    if not package:
        return jsonify({'error': 'Package not found'}), 404

    # Get service_id from association table
    service_ids = db.session.execute(
        package_service_association.select().where(package_service_association.c.package_id == package_id)
    ).fetchall()

    if not service_ids:
        return jsonify({'error': 'No services linked to this package'}), 400

    # Assuming a package is linked to only **one primary service**
    service_id = service_ids[0][1]  # Extract service_id from the result

    service = db.session.get(Service, service_id)
    if not service:
        return jsonify({'error': 'Associated service not found'}), 404

    customer = Customer.query.filter_by(id=session['user_id']).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    # Create a new service request
    new_request = ServiceRequest(
        service_id=service_id,
        service_name=service.service_name,
        pincode=customer.pincode,
        status="Requested",
        package_id=package_id,
        package_name=package_name,
        user_remark=user_remark
    )

    db.session.add(new_request)
    db.session.commit()

    return jsonify({"message": "Package booked successfully", "request_id": new_request.request_id}), 201
"""