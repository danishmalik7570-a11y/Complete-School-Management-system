from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, IntegerField, DateTimeField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, EqualTo, Length
from models import Category, Instructor

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    description = TextAreaField('Description')

class StudentForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    father_name = StringField('Father Name', validators=[DataRequired()])
    student_contact = StringField('Student Contact')
    father_contact = StringField('Father Contact')
    student_cnic = StringField('Student CNIC')
    father_cnic = StringField('Father CNIC')
    address = TextAreaField('Address')
    category_id = SelectField('Course Category', coerce=int, validators=[DataRequired()])
    total_fee = FloatField('Total Fee', validators=[DataRequired(), NumberRange(min=0)])
    advance_payment = FloatField('Advance Payment', validators=[Optional(), NumberRange(min=0)], default=0.0)
    
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

class InstructorForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone')
    address = TextAreaField('Address')
    qualification = StringField('Qualification')
    experience_years = IntegerField('Experience (Years)', validators=[Optional(), NumberRange(min=0)])
    salary = FloatField('Salary', validators=[Optional(), NumberRange(min=0)])

class ExpenseForm(FlaskForm):
    title = StringField('Expense Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('rent', 'Rent'),
        ('salary', 'Salary'),
        ('utilities', 'Utilities'),
        ('supplies', 'Supplies'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other')
    ])

class PaymentForm(FlaskForm):
    amount = FloatField('Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('online', 'Online')
    ])
    notes = TextAreaField('Notes')

class MonthlyFeeForm(FlaskForm):
    fee_month = StringField('Fee Month (YYYY-MM)', validators=[DataRequired()])
    amount_due = FloatField('Amount Due', validators=[DataRequired(), NumberRange(min=0)])
    due_date = DateTimeField('Due Date', validators=[DataRequired()], format='%Y-%m-%d')
    notes = TextAreaField('Notes')

class FeePaymentForm(FlaskForm):
    amount_paid = FloatField('Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('online', 'Online')
    ])
    notes = TextAreaField('Payment Notes')

class FeeReminderForm(FlaskForm):
    reminder_type = SelectField('Reminder Type', choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('call', 'Phone Call')
    ])
    notes = TextAreaField('Reminder Notes')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[
        ('employee', 'Employee'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('new_password', message='Passwords must match')
    ])
