import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL", "sqlite:///institute.db")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize login manager
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models
    import models
    
    # Create all tables
    db.create_all()
    
    # Create default admin user if no users exist
    from models import User
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            email='admin@dnlinstitute.com',
            full_name='System Administrator',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: admin / admin123")
    
    # Import routes and utils
    import routes
    import utils

# Add custom template filters
@app.template_filter('currency')
def currency_filter(value):
    """Format number as currency"""
    if value is None:
        return "Rs. 0.00"
    try:
        return f"Rs. {float(value):,.2f}"
    except (ValueError, TypeError):
        return "Rs. 0.00"

@app.template_filter('date')
def date_filter(value):
    """Format datetime as date"""
    if value is None:
        return ""
    if hasattr(value, 'strftime'):
        return value.strftime('%d %b %Y')
    return str(value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
