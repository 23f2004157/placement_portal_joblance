from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from config import config
from models import db, User
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['default'])

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import blueprints
from auth import auth as auth_blueprint
from admin import admin as admin_blueprint
from company import company as company_blueprint
from student import student as student_blueprint

# Register blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(company_blueprint, url_prefix='/company')
app.register_blueprint(student_blueprint, url_prefix='/student')

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

def create_admin_user():
    """Create the default admin user"""
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@placementportal.com',
                user_type='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")

def create_tables():
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    # Create database tables
    create_tables()

    # Create admin user
    create_admin_user()

    # Run the application
    app.run(debug=True)
