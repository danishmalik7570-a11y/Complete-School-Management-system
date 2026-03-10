from datetime import datetime
import logging

def format_currency(amount):
    """Format amount as currency with Rs. prefix"""
    return f"Rs. {amount:,.2f}"

def format_date(date):
    """Format date for display"""
    if isinstance(date, datetime):
        return date.strftime('%d/%m/%Y')
    return date

def format_datetime(datetime_obj):
    """Format datetime for display"""
    if isinstance(datetime_obj, datetime):
        return datetime_obj.strftime('%d/%m/%Y %I:%M %p')
    return datetime_obj

def log_action(action, user_id=None, details=None):
    """Log user actions for audit trail"""
    logging.info(f"Action: {action}, User: {user_id}, Details: {details}")

# Template filters
def register_template_filters(app):
    @app.template_filter('currency')
    def currency_filter(amount):
        return format_currency(amount)
    
    @app.template_filter('date')
    def date_filter(date):
        return format_date(date)
    
    @app.template_filter('datetime')
    def datetime_filter(datetime_obj):
        return format_datetime(datetime_obj)

# Register filters with app
from app import app
register_template_filters(app)
