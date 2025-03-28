from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session
import os
from models import db
from routes import auth_bp, admin_bp  

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Session Configuration
app.config['SESSION_TYPE'] = 'filesystem'
#app.config['SESSION_PERMANENT'] = False  
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# ✅ CORS Configuration
CORS(app, resources={r"/*": {"origins": "http://localhost:8082"}}, supports_credentials=True)

# ✅ Allow Cookies in Response
app.config['SESSION_COOKIE_HTTPONLY'] = True  
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  
app.config['SESSION_COOKIE_SECURE'] = False  

# Initialize Flask Extensions
db.init_app(app)
migrate = Migrate(app, db)
Session(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
