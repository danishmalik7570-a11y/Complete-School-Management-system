from flask import render_template, request, redirect, url_for, flash, jsonify, make_response, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import Category, Student, Instructor, InstructorCategory, Payment, Expense, MonthlyFee, FeeReminder, User
from forms import CategoryForm, StudentForm, InstructorForm, ExpenseForm, PaymentForm, MonthlyFeeForm, FeePaymentForm, FeeReminderForm, LoginForm, UserForm, ChangePasswordForm
from datetime import datetime, timedelta
from sqlalchemy import func
import logging
import calendar

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_active:
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Your account is deactivated. Please contact admin.', 'error')
        else:
            flash('Invalid username or password.', 'error')
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

# User Management Routes (Admin only)
@app.route('/users')
@login_required
def users():
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('users/index.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    form = UserForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Username or email already exists.', 'error')
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'User {user.username} created successfully!', 'success')
            return redirect(url_for('users'))
    
    return render_template('users/add.html', form=form)

@app.route('/profile')
@login_required
def profile():
    return render_template('users/profile.html', user=current_user)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('users/change_password.html', form=form)

@app.route('/')
@login_required
def dashboard():
    # Calculate dashboard statistics
    total_students = Student.query.filter_by(is_active=True).count()
    total_instructors = Instructor.query.filter_by(is_active=True).count()
    
    # Calculate financial data (only for admins)
    total_revenue = 0
    total_expenses = 0
    net_profit = 0
    
    if current_user.can_view_financial_data():
        # Calculate total revenue from all sources
        regular_payments = db.session.query(func.sum(Payment.amount)).scalar() or 0
        monthly_fee_payments = db.session.query(func.sum(MonthlyFee.amount_paid)).scalar() or 0
        advance_payments = db.session.query(func.sum(Student.advance_payment)).scalar() or 0
        total_revenue = regular_payments + monthly_fee_payments + advance_payments
        
        # Calculate total expenses
        total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
        
        # Calculate net profit
        net_profit = total_revenue - total_expenses
    
    # Recent students (last 5)
    recent_students = Student.query.order_by(Student.admission_date.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         total_students=total_students,
                         total_instructors=total_instructors,
                         total_revenue=total_revenue,
                         total_expenses=total_expenses,
                         net_profit=net_profit,
                         recent_students=recent_students,
                         can_view_financial=current_user.can_view_financial_data())

# Category Routes
@app.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('categories/index.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('categories'))
    return render_template('categories/form.html', form=form, title='Add Category')

@app.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('categories'))
    return render_template('categories/form.html', form=form, title='Edit Category')

@app.route('/categories/delete/<int:id>')
def delete_category(id):
    category = Category.query.get_or_404(id)
    if category.students:
        flash('Cannot delete category with enrolled students!', 'error')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    return redirect(url_for('categories'))

# Student Routes
@app.route('/students')
def students():
    page = request.args.get('page', 1, type=int)
    students = Student.query.filter_by(is_active=True).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('students/index.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        # Calculate monthly installment (total fee - advance payment) / 6 months
        advance_payment = form.advance_payment.data or 0
        remaining_fee = form.total_fee.data - advance_payment
        monthly_installment = remaining_fee / 6
        
        student = Student(
            full_name=form.full_name.data,
            father_name=form.father_name.data,
            student_contact=form.student_contact.data,
            father_contact=form.father_contact.data,
            student_cnic=form.student_cnic.data,
            father_cnic=form.father_cnic.data,
            address=form.address.data,
            category_id=form.category_id.data,
            total_fee=form.total_fee.data,
            advance_payment=advance_payment,
            monthly_installment=monthly_installment
        )
        db.session.add(student)
        db.session.flush()  # Get the student ID
        
        # Create 6 monthly fee records
        create_monthly_fees(student)
        
        db.session.commit()
        flash('Student added successfully with fee schedule created!', 'success')
        return redirect(url_for('student_fees', id=student.id))
    return render_template('students/form.html', form=form, title='Add Student')

def create_monthly_fees(student):
    """Create 6 monthly fee records for a student"""
    current_month = datetime.now().replace(day=1)
    
    for i in range(6):
        fee_month = current_month + timedelta(days=32 * i)
        fee_month = fee_month.replace(day=1)
        
        # Set due date to the 10th of each month
        due_date = fee_month.replace(day=10)
        
        monthly_fee = MonthlyFee(
            student_id=student.id,
            fee_month=fee_month.strftime('%Y-%m'),
            amount_due=student.monthly_installment,
            due_date=due_date
        )
        db.session.add(monthly_fee)

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    if form.validate_on_submit():
        student.full_name = form.full_name.data
        student.father_name = form.father_name.data
        student.student_contact = form.student_contact.data
        student.father_contact = form.father_contact.data
        student.student_cnic = form.student_cnic.data
        student.father_cnic = form.father_cnic.data
        student.address = form.address.data
        student.category_id = form.category_id.data
        student.total_fee = form.total_fee.data
        student.advance_payment = form.advance_payment.data or 0
        remaining_fee = form.total_fee.data - student.advance_payment
        student.monthly_installment = remaining_fee / 6
        
        # Update existing monthly fees with new amount
        for monthly_fee in student.monthly_fees:
            if not monthly_fee.is_paid:
                monthly_fee.amount_due = student.monthly_installment
        
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('students'))
    return render_template('students/form.html', form=form, title='Edit Student')

@app.route('/students/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    student.is_active = False
    db.session.commit()
    flash('Student deactivated successfully!', 'success')
    return redirect(url_for('students'))

@app.route('/students/<int:id>/payment', methods=['GET', 'POST'])
def add_payment(id):
    student = Student.query.get_or_404(id)
    form = PaymentForm()
    if form.validate_on_submit():
        payment = Payment(
            student_id=student.id,
            amount=form.amount.data,
            payment_method=form.payment_method.data,
            notes=form.notes.data
        )
        db.session.add(payment)
        db.session.commit()
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('students'))
    return render_template('students/payment_form.html', form=form, student=student)

@app.route('/students/<int:id>/admission-slip')
def admission_slip(id):
    student = Student.query.get_or_404(id)
    return render_template('students/admission_slip.html', student=student)

# Instructor Routes
@app.route('/instructors')
def instructors():
    instructors = Instructor.query.filter_by(is_active=True).all()
    return render_template('instructors/index.html', instructors=instructors)

@app.route('/instructors/add', methods=['GET', 'POST'])
def add_instructor():
    form = InstructorForm()
    if form.validate_on_submit():
        instructor = Instructor(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            qualification=form.qualification.data,
            experience_years=form.experience_years.data,
            salary=form.salary.data
        )
        db.session.add(instructor)
        db.session.commit()
        flash('Instructor added successfully!', 'success')
        return redirect(url_for('instructors'))
    return render_template('instructors/form.html', form=form, title='Add Instructor')

@app.route('/instructors/edit/<int:id>', methods=['GET', 'POST'])
def edit_instructor(id):
    instructor = Instructor.query.get_or_404(id)
    form = InstructorForm(obj=instructor)
    if form.validate_on_submit():
        instructor.full_name = form.full_name.data
        instructor.email = form.email.data
        instructor.phone = form.phone.data
        instructor.address = form.address.data
        instructor.qualification = form.qualification.data
        instructor.experience_years = form.experience_years.data
        instructor.salary = form.salary.data
        db.session.commit()
        flash('Instructor updated successfully!', 'success')
        return redirect(url_for('instructors'))
    return render_template('instructors/form.html', form=form, title='Edit Instructor')

@app.route('/instructors/delete/<int:id>')
def delete_instructor(id):
    instructor = Instructor.query.get_or_404(id)
    instructor.is_active = False
    db.session.commit()
    flash('Instructor deactivated successfully!', 'success')
    return redirect(url_for('instructors'))

# Finance Routes (Admin Only)
@app.route('/finance')
@login_required
def finance():
    if not current_user.can_view_financial_data():
        flash('You do not have permission to access financial data.', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculate financial statistics - include all revenue sources
    regular_payments = db.session.query(func.sum(Payment.amount)).scalar() or 0
    monthly_fee_payments = db.session.query(func.sum(MonthlyFee.amount_paid)).scalar() or 0
    advance_payments = db.session.query(func.sum(Student.advance_payment)).scalar() or 0
    total_revenue = regular_payments + monthly_fee_payments + advance_payments
    
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    net_profit = total_revenue - total_expenses
    
    # Get recent expenses
    recent_expenses = Expense.query.order_by(Expense.expense_date.desc()).limit(10).all()
    
    return render_template('finance/index.html',
                         total_revenue=total_revenue,
                         regular_payments=regular_payments,
                         monthly_fee_payments=monthly_fee_payments,
                         advance_payments=advance_payments,
                         total_expenses=total_expenses,
                         net_profit=net_profit,
                         recent_expenses=recent_expenses)

@app.route('/finance/expense/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if not current_user.can_view_financial_data():
        flash('You do not have permission to access financial data.', 'error')
        return redirect(url_for('dashboard'))
    
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            title=form.title.data,
            description=form.description.data,
            amount=form.amount.data,
            category=form.category.data
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('finance'))
    return render_template('finance/expense_form.html', form=form, title='Add Expense')

@app.route('/finance/expense/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    form = ExpenseForm(obj=expense)
    if form.validate_on_submit():
        expense.title = form.title.data
        expense.description = form.description.data
        expense.amount = form.amount.data
        expense.category = form.category.data
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('finance'))
    return render_template('finance/expense_form.html', form=form, title='Edit Expense')

@app.route('/finance/expense/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('finance'))

# Fee Management Routes
@app.route('/students/<int:id>/fees')
def student_fees(id):
    student = Student.query.get_or_404(id)
    monthly_fees = MonthlyFee.query.filter_by(student_id=id).order_by(MonthlyFee.due_date).all()
    
    # Update overdue status
    current_date = datetime.now()
    for fee in monthly_fees:
        if not fee.is_paid and fee.due_date < current_date:
            fee.is_overdue = True
    db.session.commit()
    
    return render_template('students/fees.html', student=student, monthly_fees=monthly_fees)

@app.route('/students/<int:student_id>/fees/<int:fee_id>/pay', methods=['GET', 'POST'])
def pay_monthly_fee(student_id, fee_id):
    student = Student.query.get_or_404(student_id)
    monthly_fee = MonthlyFee.query.get_or_404(fee_id)
    form = FeePaymentForm()
    
    if form.validate_on_submit():
        payment_amount = form.amount_paid.data
        
        # Update monthly fee
        monthly_fee.amount_paid = (monthly_fee.amount_paid or 0) + payment_amount
        if monthly_fee.amount_paid >= monthly_fee.amount_due:
            monthly_fee.is_paid = True
            monthly_fee.paid_date = datetime.now()
        
        # Create payment record
        payment = Payment(
            student_id=student_id,
            amount=payment_amount,
            payment_method=form.payment_method.data,
            notes=f"Monthly fee payment for {monthly_fee.fee_month}"
        )
        db.session.add(payment)
        db.session.commit()
        
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('student_fees', id=student_id))
    
    return render_template('students/pay_fee.html', form=form, student=student, monthly_fee=monthly_fee)

@app.route('/students/<int:student_id>/fees/add', methods=['GET', 'POST'])
def add_monthly_fee(student_id):
    student = Student.query.get_or_404(student_id)
    form = MonthlyFeeForm()
    
    if form.validate_on_submit():
        monthly_fee = MonthlyFee(
            student_id=student_id,
            fee_month=form.fee_month.data,
            amount_due=form.amount_due.data,
            due_date=form.due_date.data,
            notes=form.notes.data
        )
        db.session.add(monthly_fee)
        db.session.commit()
        flash('Monthly fee added successfully!', 'success')
        return redirect(url_for('student_fees', id=student_id))
    
    return render_template('students/add_monthly_fee.html', form=form, student=student)

@app.route('/students/<int:student_id>/fees/<int:fee_id>/reminder', methods=['GET', 'POST'])
def send_fee_reminder(student_id, fee_id):
    student = Student.query.get_or_404(student_id)
    monthly_fee = MonthlyFee.query.get_or_404(fee_id)
    form = FeeReminderForm()
    
    if form.validate_on_submit():
        reminder = FeeReminder(
            student_id=student_id,
            monthly_fee_id=fee_id,
            reminder_type=form.reminder_type.data,
            notes=form.notes.data,
            is_sent=True  # In real app, this would be set after actually sending
        )
        db.session.add(reminder)
        db.session.commit()
        flash(f'{form.reminder_type.data.title()} reminder sent successfully!', 'success')
        return redirect(url_for('student_fees', id=student_id))
    
    return render_template('students/send_reminder.html', form=form, student=student, monthly_fee=monthly_fee)

@app.route('/fees/overdue')
def overdue_fees():
    current_date = datetime.now()
    overdue_fees = MonthlyFee.query.filter(
        MonthlyFee.is_paid == False,
        MonthlyFee.due_date < current_date
    ).join(Student).order_by(MonthlyFee.due_date).all()
    
    return render_template('finance/overdue_fees.html', overdue_fees=overdue_fees)

@app.route('/fees/report')
def fee_report():
    # Fee collection statistics
    total_fees_due = db.session.query(func.sum(MonthlyFee.amount_due)).scalar() or 0
    total_fees_paid = db.session.query(func.sum(MonthlyFee.amount_paid)).scalar() or 0
    total_advance_payments = db.session.query(func.sum(Student.advance_payment)).scalar() or 0
    
    overdue_count = MonthlyFee.query.filter(
        MonthlyFee.is_paid == False,
        MonthlyFee.due_date < datetime.now()
    ).count()
    
    # Monthly breakdown
    monthly_stats = db.session.query(
        MonthlyFee.fee_month,
        func.sum(MonthlyFee.amount_due).label('total_due'),
        func.sum(MonthlyFee.amount_paid).label('total_paid')
    ).group_by(MonthlyFee.fee_month).order_by(MonthlyFee.fee_month).all()
    
    return render_template('finance/fee_report.html',
                         total_fees_due=total_fees_due,
                         total_fees_paid=total_fees_paid,
                         total_advance_payments=total_advance_payments,
                         overdue_count=overdue_count,
                         monthly_stats=monthly_stats)
