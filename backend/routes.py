from flask import Blueprint, request, jsonify, session
from models import db, User, Service,  ServingPincode
from flask_cors import CORS

# Define blueprints first
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)

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


'''
@admin_bp.route('/add_service', methods=['POST'])
def add_service():
    print("Session Data at add_service:", dict(session))  # Debugging

    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403  # This is causing 403

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
'''



@auth_bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    role = session.get('role')
    return jsonify({'role': role}), 200

@admin_bp.route("/services", methods=["GET"])
def get_services():
    if 'role' not in session or session['role'] != 'admin':
        print("❌ Unauthorized - session missing:", dict(session))  # Debugging unauthorized issue
        return jsonify({'error': 'Unauthorized'}), 403

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


"""@admin_bp.route('/add_service', methods=['POST'])
def add_service():
    print("Session Data at add_service:", dict(session))  # 🔍 Debug session before checking role

    if 'role' not in session or session['role'] != 'admin':
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
"""