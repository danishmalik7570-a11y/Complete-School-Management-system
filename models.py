from app import db
from datetime import datetime
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')  # 'admin' or 'employee'
    full_name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def can_view_financial_data(self):
        return self.role == 'admin'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='category', lazy=True)
    instructors = db.relationship('InstructorCategory', backref='category', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    student_contact = db.Column(db.String(15))
    father_contact = db.Column(db.String(15))
    student_cnic = db.Column(db.String(15))
    father_cnic = db.Column(db.String(15))
    address = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    batch_timing = db.Column(db.DateTime, default=datetime.utcnow)
    total_fee = db.Column(db.Float, nullable=False)
    advance_payment = db.Column(db.Float, default=0.0)
    monthly_installment = db.Column(db.Float, nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    payments = db.relationship('Payment', backref='student', lazy=True, cascade='all, delete-orphan')
    monthly_fees = db.relationship('MonthlyFee', backref='student', lazy=True, cascade='all, delete-orphan')
    
    @property
    def total_paid(self):
        advance = self.advance_payment or 0
        monthly_payments = sum(fee.amount_paid for fee in self.monthly_fees if fee.amount_paid)
        return advance + monthly_payments
    
    @property
    def remaining_balance(self):
        return self.total_fee - self.total_paid
    
    @property
    def last_paid_month(self):
        paid_fees = [fee for fee in self.monthly_fees if fee.is_paid]
        if paid_fees:
            return max(paid_fees, key=lambda x: x.due_date).fee_month
        return None
    
    @property
    def next_due_month(self):
        unpaid_fees = [fee for fee in self.monthly_fees if not fee.is_paid]
        if unpaid_fees:
            return min(unpaid_fees, key=lambda x: x.due_date)
        return None
    
    @property
    def total_months_due(self):
        return len([fee for fee in self.monthly_fees if not fee.is_paid])

class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    salary = db.Column(db.Float)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    categories = db.relationship('InstructorCategory', backref='instructor', lazy=True)

class InstructorCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), default='Cash')
    notes = db.Column(db.Text)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))  # rent, salary, utilities, etc.
    
class MonthlyFee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    fee_month = db.Column(db.String(7), nullable=False)  # Format: YYYY-MM
    amount_due = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    due_date = db.Column(db.DateTime, nullable=False)
    paid_date = db.Column(db.DateTime)
    is_paid = db.Column(db.Boolean, default=False)
    is_overdue = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def remaining_amount(self):
        return self.amount_due - (self.amount_paid or 0)
    
    @property
    def is_partially_paid(self):
        return (self.amount_paid or 0) > 0 and (self.amount_paid or 0) < self.amount_due
    
    @property
    def payment_status(self):
        if self.is_paid:
            return "Paid"
        elif self.is_partially_paid:
            return "Partial"
        elif self.is_overdue:
            return "Overdue"
        else:
            return "Pending"
    
    @property
    def days_overdue(self):
        """Calculate how many days the fee is overdue"""
        if self.is_paid or not self.due_date:
            return 0
        today = datetime.now().date()
        due_date = self.due_date.date() if hasattr(self.due_date, 'date') else self.due_date
        if due_date < today:
            return (today - due_date).days
        return 0

class FeeReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    monthly_fee_id = db.Column(db.Integer, db.ForeignKey('monthly_fee.id'), nullable=False)
    reminder_date = db.Column(db.DateTime, default=datetime.utcnow)
    reminder_type = db.Column(db.String(20), default='email')  # email, sms, call
    is_sent = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    # Relationships
    student = db.relationship('Student', backref='fee_reminders')
    monthly_fee = db.relationship('MonthlyFee', backref='reminders')

class Revenue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
