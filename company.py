from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from forms import CompanyProfileForm, PlacementDriveForm, ApplicationStatusForm
from models import db, Company, PlacementDrive, Application, Student
from functools import wraps
from datetime import datetime

company = Blueprint('company', __name__)

def company_required(f):
    """Decorator to ensure user is a company"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'company':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@company.route('/dashboard')
@login_required
@company_required
def dashboard():
    """Company dashboard"""
    # Get company profile
    company_profile = Company.query.filter_by(user_id=current_user.id).first()
    if not company_profile:
        flash('Company profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    # Check if company is approved
    if company_profile.approval_status != 'approved':
        flash('Your company registration is pending approval from the admin.', 'warning')
        return render_template('company/pending_approval.html', company=company_profile)

    # Get placement drives and applicant counts
    drives = PlacementDrive.query.filter_by(company_id=company_profile.id).all()
    drive_data = []
    for drive in drives:
        applicant_count = Application.query.filter_by(drive_id=drive.id).count()
        drive_data.append({
            'drive': drive,
            'applicant_count': applicant_count
        })

    return render_template('company/dashboard.html', 
                          company=company_profile, 
                          drive_data=drive_data)

@company.route('/profile', methods=['GET', 'POST'])
@login_required
@company_required
def profile():
    """View and edit company profile"""
    company_profile = Company.query.filter_by(user_id=current_user.id).first()
    if not company_profile:
        flash('Company profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    form = CompanyProfileForm(obj=company_profile)
    if form.validate_on_submit():
        company_profile.company_name = form.company_name.data
        company_profile.hr_contact = form.hr_contact.data
        company_profile.hr_email = form.hr_email.data
        company_profile.website = form.website.data
        company_profile.description = form.description.data
        company_profile.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Company profile updated successfully!', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/profile.html', form=form, company=company_profile)

@company.route('/drives')
@login_required
@company_required
def drives():
    """View all placement drives created by the company"""
    company_profile = Company.query.filter_by(user_id=current_user.id).first()
    if not company_profile:
        flash('Company profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    drives = PlacementDrive.query.filter_by(company_id=company_profile.id).order_by(
        PlacementDrive.created_at.desc()
    ).all()

    return render_template('company/drives.html', drives=drives, company=company_profile)

@company.route('/drives/create', methods=['GET', 'POST'])
@login_required
@company_required
def create_drive():
    """Create a new placement drive"""
    company_profile = Company.query.filter_by(user_id=current_user.id).first()
    if not company_profile:
        flash('Company profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    form = PlacementDriveForm()
    if form.validate_on_submit():
        drive = PlacementDrive(
            company_id=company_profile.id,
            job_title=form.job_title.data,
            job_description=form.job_description.data,
            eligibility_criteria=form.eligibility_criteria.data,
            application_deadline=datetime.combine(form.application_deadline.data, datetime.min.time()),
            salary_package=form.salary_package.data,
            location=form.location.data,
            status='pending'  # Default status
        )
        db.session.add(drive)
        db.session.commit()

        flash('Placement drive created successfully! It will be visible to students after admin approval.', 'success')
        return redirect(url_for('company.drives'))

    return render_template('company/create_drive.html', form=form, company=company_profile)

@company.route('/drives/<int:drive_id>/edit', methods=['GET', 'POST'])
@login_required
@company_required
def edit_drive(drive_id):
    """Edit an existing placement drive"""
    company_profile = Company.query.filter_by(user_id=current_user.id).first()
    if not company_profile:
        flash('Company profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    drive = PlacementDrive.query.get_or_404(drive_id)

    # Check if the drive belongs to this company
    if drive.company_id != company_profile.id:
        flash('You do not have permission to edit this drive.', 'danger')
        return redirect(url_for('company.drives'))

    form = PlacementDriveForm(obj=drive)
    if form.validate_on_submit():
        drive.job_title = form.job_title.data
        drive.job_description = form.job_description.data
        drive.eligibility_criteria = form.eligibility_criteria.data
        drive.application_deadline = datetime.combine(form.application_deadline.data, datetime.min.time())
        drive.salary_package = form.salary_package.data
        drive.location = form.location.data
        drive.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Placement drive updated successfully!', 'success')
        return redirect(url_for('company.drives'))

    return render_template('company/edit_drive.html', form=form, drive=drive, company=company_profile)

@company.route('/drives/<int:drive_id>/delete', methods=['POST'])
@login_required
@company_required
def delete_drive(drive_id):
    """Delete a placement drive"""
    company_profile = Company.query.filter_by(user_id=current_user.id).first()
    if not company_profile:
        flash('Company profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    drive = PlacementDrive.query.get_or_404(drive_id)

    # Check if the drive belongs to this company
    if drive.company_id != company_profile.id:
        flash('You do not have permission to delete this drive.', 'danger')
        return redirect(url_for('company.drives'))

    # Delete all applications for this drive
    Application.query.filter_by(drive_id=drive_id).delete()

    db.session.delete(drive)
    db.session.commit()

    flash('Placement drive deleted successfully!', 'success')
    return redirect(url_for('company.drives'))

@company.route('/drives/<int:drive_id>/close', methods=['POST'])
@login_required
@company_required
def close_drive(drive_id):
    """Close a placement drive"""
    company_profile = Company.query.filter_by(user_id=current_user.id).first()
    if not company_profile:
        flash('Company profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    drive = PlacementDrive.query.get_or_404(drive_id)

    # Check if the drive belongs to this company
    if drive.company_id != company_profile.id:
        flash('You do not have permission to close this drive.', 'danger')
        return redirect(url_for('company.drives'))

    drive.status = 'closed'
    db.session.commit()

    flash('Placement drive closed successfully!', 'success')
    return redirect(url_for('company.drives'))

@company.route('/drives/<int:drive_id>/applications')
@login_required
@company_required
def drive_applications(drive_id):
    """View applications for a specific drive"""
    company_profile = Company.query.filter_by(user_id=current_user.id).first()
    if not company_profile:
        flash('Company profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    drive = PlacementDrive.query.get_or_404(drive_id)

    # Check if the drive belongs to this company
    if drive.company_id != company_profile.id:
        flash('You do not have permission to view applications for this drive.', 'danger')
        return redirect(url_for('company.drives'))

    applications = Application.query.filter_by(drive_id=drive_id).all()

    return render_template('company/drive_applications.html', 
                          drive=drive, 
                          applications=applications,
                          company=company_profile)

@company.route('/applications/<int:application_id>/update', methods=['GET', 'POST'])
@login_required
@company_required
def update_application(application_id):
    """Update application status"""
    company_profile = Company.query.filter_by(user_id=current_user.id).first()
    if not company_profile:
        flash('Company profile not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.login'))

    application = Application.query.get_or_404(application_id)
    drive = PlacementDrive.query.get_or_404(application.drive_id)

    # Check if the drive belongs to this company
    if drive.company_id != company_profile.id:
        flash('You do not have permission to update this application.', 'danger')
        return redirect(url_for('company.drives'))

    form = ApplicationStatusForm(obj=application)
    if form.validate_on_submit():
        application.status = form.status.data
        application.notes = form.notes.data
        application.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Application status updated successfully!', 'success')
        return redirect(url_for('company.drive_applications', drive_id=drive.id))

    return render_template('company/update_application.html', 
                          form=form, 
                          application=application,
                          drive=drive,
                          company=company_profile)
