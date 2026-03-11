from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from forms import StudentProfileForm
from models import db, Student, PlacementDrive, Application
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
import os

student = Blueprint('student', __name__)

def student_required(f):
    """Decorator to ensure user is a student"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'student':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard"""
    # Get student profile
    student_profile = Student.query.filter_by(user_id=current_user.id).first()
    if not student_profile:
        flash('Student profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    # Get approved placement drives
    approved_drives = PlacementDrive.query.filter_by(status='approved').all()

    # Get student's applications
    applications = Application.query.filter_by(student_id=student_profile.id).all()

    # Get applied drive IDs
    applied_drive_ids = [app.drive_id for app in applications]

    return render_template('student/dashboard.html', 
                          student=student_profile,
                          approved_drives=approved_drives,
                          applications=applications,
                          applied_drive_ids=applied_drive_ids)

@student.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    """View and edit student profile"""
    student_profile = Student.query.filter_by(user_id=current_user.id).first()
    if not student_profile:
        flash('Student profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    form = StudentProfileForm(obj=student_profile)
    if form.validate_on_submit():
        # Handle resume upload
        if form.resume.data:
            from app import app
            filename = secure_filename(f"{current_user.username}_{form.resume.data.filename}")
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.resume.data.save(resume_path)
            # Store relative path
            student_profile.resume_path = os.path.join('uploads', filename)

        student_profile.student_id = form.student_id.data
        student_profile.full_name = form.full_name.data
        student_profile.email = form.email.data
        student_profile.phone = form.phone.data
        student_profile.department = form.department.data
        student_profile.year = form.year.data
        student_profile.cgpa = form.cgpa.data
        student_profile.skills = form.skills.data
        student_profile.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('student/profile.html', form=form, student=student_profile)

@student.route('/drives')
@login_required
@student_required
def drives():
    """View all approved placement drives"""
    student_profile = Student.query.filter_by(user_id=current_user.id).first()
    if not student_profile:
        flash('Student profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    # Get all approved placement drives
    approved_drives = PlacementDrive.query.filter_by(status='approved').order_by(
        PlacementDrive.application_deadline.asc()
    ).all()

    # Get student's applications
    applications = Application.query.filter_by(student_id=student_profile.id).all()

    # Get applied drive IDs
    applied_drive_ids = [app.drive_id for app in applications]

    return render_template('student/drives.html', 
                          student=student_profile,
                          approved_drives=approved_drives,
                          applied_drive_ids=applied_drive_ids)

@student.route('/drives/<int:drive_id>/apply', methods=['POST'])
@login_required
@student_required
def apply_drive(drive_id):
    """Apply for a placement drive"""
    student_profile = Student.query.filter_by(user_id=current_user.id).first()
    if not student_profile:
        flash('Student profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    drive = PlacementDrive.query.get_or_404(drive_id)

    # Check if drive is approved
    if drive.status != 'approved':
        flash('This drive is not currently accepting applications.', 'warning')
        return redirect(url_for('student.drives'))

    # Check if application deadline has passed
    if drive.application_deadline < datetime.utcnow():
        flash('The application deadline for this drive has passed.', 'warning')
        return redirect(url_for('student.drives'))

    # Check if student has already applied
    existing_application = Application.query.filter_by(
        student_id=student_profile.id,
        drive_id=drive_id
    ).first()

    if existing_application:
        flash('You have already applied for this drive.', 'info')
        return redirect(url_for('student.drives'))

    # Create new application
    application = Application(
        student_id=student_profile.id,
        drive_id=drive_id,
        status='applied'
    )
    db.session.add(application)
    db.session.commit()

    flash('Application submitted successfully!', 'success')
    return redirect(url_for('student.drives'))

@student.route('/applications')
@login_required
@student_required
def applications():
    """View all applications"""
    student_profile = Student.query.filter_by(user_id=current_user.id).first()
    if not student_profile:
        flash('Student profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    # Get all applications for this student
    applications = Application.query.filter_by(student_id=student_profile.id).order_by(
        Application.application_date.desc()
    ).all()

    return render_template('student/applications.html', 
                          student=student_profile,
                          applications=applications)

@student.route('/applications/<int:application_id>')
@login_required
@student_required
def application_detail(application_id):
    """View application details"""
    student_profile = Student.query.filter_by(user_id=current_user.id).first()
    if not student_profile:
        flash('Student profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    application = Application.query.get_or_404(application_id)

    # Check if application belongs to this student
    if application.student_id != student_profile.id:
        flash('You do not have permission to view this application.', 'danger')
        return redirect(url_for('student.applications'))

    drive = PlacementDrive.query.get_or_404(application.drive_id)

    return render_template('student/application_detail.html', 
                          student=student_profile,
                          application=application,
                          drive=drive)

@student.route('/history')
@login_required
@student_required
def history():
    """View placement history"""
    student_profile = Student.query.filter_by(user_id=current_user.id).first()
    if not student_profile:
        flash('Student profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    # Get all applications for this student
    applications = Application.query.filter_by(student_id=student_profile.id).order_by(
        Application.application_date.desc()
    ).all()

    # Filter for completed applications (selected or rejected)
    history = [app for app in applications if app.status in ['selected', 'rejected']]

    return render_template('student/history.html', 
                          student=student_profile,
                          history=history)
