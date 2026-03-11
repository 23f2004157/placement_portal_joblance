from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm, RegistrationForm, CompanyProfileForm, StudentProfileForm
from models import db, User, Company, Student
from werkzeug.utils import secure_filename
import os
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        # Redirect to appropriate dashboard based on user type
        if current_user.user_type == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.user_type == 'company':
            return redirect(url_for('company.dashboard'))
        elif current_user.user_type == 'student':
            return redirect(url_for('student.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            # Check if user is blacklisted
            if user.is_blacklisted:
                flash('Your account has been blacklisted. Please contact the administrator.', 'danger')
                return render_template('auth/login.html', form=form)

            # Check if company is approved
            if user.user_type == 'company':
                company = Company.query.filter_by(user_id=user.id).first()
                if company and company.approval_status != 'approved':
                    flash('Your company registration is pending approval from the admin.', 'warning')
                    return render_template('auth/login.html', form=form)

            login_user(user)
            next_page = request.args.get('next')

            # Redirect to appropriate dashboard based on user type
            if user.user_type == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
            elif user.user_type == 'company':
                return redirect(next_page or url_for('company.dashboard'))
            elif user.user_type == 'student':
                return redirect(next_page or url_for('student.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            user_type=form.user_type.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Create profile based on user type
        if form.user_type.data == 'company':
            return redirect(url_for('auth.company_profile', user_id=user.id))
        else:
            return redirect(url_for('auth.student_profile', user_id=user.id))

    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/company-profile/<int:user_id>', methods=['GET', 'POST'])
def company_profile(user_id):
    """Handle company profile creation"""
    user = User.query.get_or_404(user_id)

    # Check if user already has a profile
    existing_profile = Company.query.filter_by(user_id=user_id).first()
    if existing_profile:
        flash('Company profile already exists.', 'info')
        return redirect(url_for('auth.login'))

    form = CompanyProfileForm()
    if form.validate_on_submit():
        company = Company(
            user_id=user_id,
            company_name=form.company_name.data,
            hr_contact=form.hr_contact.data,
            hr_email=form.hr_email.data,
            website=form.website.data,
            description=form.description.data,
            approval_status='pending'  # Default status
        )
        db.session.add(company)
        db.session.commit()

        flash('Registration successful! Your account is pending approval from the admin.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/company_profile.html', form=form, user=user)

@auth.route('/student-profile/<int:user_id>', methods=['GET', 'POST'])
def student_profile(user_id):
    """Handle student profile creation"""
    user = User.query.get_or_404(user_id)

    # Check if user already has a profile
    existing_profile = Student.query.filter_by(user_id=user_id).first()
    if existing_profile:
        flash('Student profile already exists.', 'info')
        return redirect(url_for('auth.login'))

    form = StudentProfileForm()
    if form.validate_on_submit():
        # Handle resume upload
        resume_path = None
        if form.resume.data:
            from app import app
            filename = secure_filename(f"{user.username}_{form.resume.data.filename}")
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.resume.data.save(resume_path)
            # Store relative path
            resume_path = os.path.join('uploads', filename)

        student = Student(
            user_id=user_id,
            student_id=form.student_id.data,
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            department=form.department.data,
            year=form.year.data,
            cgpa=form.cgpa.data,
            skills=form.skills.data,
            resume_path=resume_path
        )
        db.session.add(student)
        db.session.commit()

        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/student_profile.html', form=form, user=user)
