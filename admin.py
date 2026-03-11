from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from forms import SearchForm
from models import db, User, Company, Student, PlacementDrive, Application
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to ensure user is an admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    # Get statistics
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_applications = Application.query.count()
    total_drives = PlacementDrive.query.count()

    # Get pending approvals
    pending_companies = Company.query.filter_by(approval_status='pending').count()
    pending_drives = PlacementDrive.query.filter_by(status='pending').count()

    return render_template('admin/dashboard.html',
                          total_students=total_students,
                          total_companies=total_companies,
                          total_applications=total_applications,
                          total_drives=total_drives,
                          pending_companies=pending_companies,
                          pending_drives=pending_drives)

@admin.route('/companies')
@login_required
@admin_required
def companies():
    """View all companies"""
    page = request.args.get('page', 1, type=int)
    companies = Company.query.order_by(Company.created_at.desc()).paginate(
        page=page, per_page=10
    )
    return render_template('admin/companies.html', companies=companies)

@admin.route('/companies/<int:company_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_company(company_id):
    """Approve a company registration"""
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'approved'
    db.session.commit()
    flash(f'{company.company_name} has been approved.', 'success')
    return redirect(url_for('admin.companies'))

@admin.route('/companies/<int:company_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_company(company_id):
    """Reject a company registration"""
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'rejected'
    db.session.commit()
    flash(f'{company.company_name} has been rejected.', 'warning')
    return redirect(url_for('admin.companies'))

@admin.route('/companies/<int:company_id>/blacklist', methods=['POST'])
@login_required
@admin_required
def blacklist_company(company_id):
    """Blacklist a company"""
    company = Company.query.get_or_404(company_id)
    user = User.query.get_or_404(company.user_id)
    user.is_blacklisted = True
    db.session.commit()
    flash(f'{company.company_name} has been blacklisted.', 'warning')
    return redirect(url_for('admin.companies'))

@admin.route('/companies/<int:company_id>/unblacklist', methods=['POST'])
@login_required
@admin_required
def unblacklist_company(company_id):
    """Unblacklist a company"""
    company = Company.query.get_or_404(company_id)
    user = User.query.get_or_404(company.user_id)
    user.is_blacklisted = False
    db.session.commit()
    flash(f'{company.company_name} has been unblacklisted.', 'success')
    return redirect(url_for('admin.companies'))

@admin.route('/students')
@login_required
@admin_required
def students():
    """View all students"""
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', None)

    if search_term:
        # Search by name, student ID, or email
        students = Student.query.filter(
            (Student.full_name.contains(search_term)) |
            (Student.student_id.contains(search_term)) |
            (Student.email.contains(search_term))
        ).paginate(page=page, per_page=10)
    else:
        students = Student.query.order_by(Student.created_at.desc()).paginate(
            page=page, per_page=10
        )

    form = SearchForm()
    return render_template('admin/students.html', students=students, form=form, search_term=search_term)

@admin.route('/students/<int:student_id>/blacklist', methods=['POST'])
@login_required
@admin_required
def blacklist_student(student_id):
    """Blacklist a student"""
    student = Student.query.get_or_404(student_id)
    user = User.query.get_or_404(student.user_id)
    user.is_blacklisted = True
    db.session.commit()
    flash(f'{student.full_name} has been blacklisted.', 'warning')
    return redirect(url_for('admin.students'))

@admin.route('/students/<int:student_id>/unblacklist', methods=['POST'])
@login_required
@admin_required
def unblacklist_student(student_id):
    """Unblacklist a student"""
    student = Student.query.get_or_404(student_id)
    user = User.query.get_or_404(student.user_id)
    user.is_blacklisted = False
    db.session.commit()
    flash(f'{student.full_name} has been unblacklisted.', 'success')
    return redirect(url_for('admin.students'))

@admin.route('/students/<int:student_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    """Delete a student"""
    student = Student.query.get_or_404(student_id)
    user = User.query.get_or_404(student.user_id)

    # Delete student's applications
    Application.query.filter_by(student_id=student_id).delete()

    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()

    flash(f'{student.full_name} has been deleted.', 'success')
    return redirect(url_for('admin.students'))

@admin.route('/drives')
@login_required
@admin_required
def drives():
    """View all placement drives"""
    page = request.args.get('page', 1, type=int)
    drives = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).paginate(
        page=page, per_page=10
    )
    return render_template('admin/drives.html', drives=drives)

@admin.route('/drives/<int:drive_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_drive(drive_id):
    """Approve a placement drive"""
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'approved'
    db.session.commit()
    flash(f'{drive.job_title} has been approved.', 'success')
    return redirect(url_for('admin.drives'))

@admin.route('/drives/<int:drive_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_drive(drive_id):
    """Reject a placement drive"""
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'rejected'
    db.session.commit()
    flash(f'{drive.job_title} has been rejected.', 'warning')
    return redirect(url_for('admin.drives'))

@admin.route('/drives/<int:drive_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_drive(drive_id):
    """Delete a placement drive"""
    drive = PlacementDrive.query.get_or_404(drive_id)

    # Delete all applications for this drive
    Application.query.filter_by(drive_id=drive_id).delete()

    db.session.delete(drive)
    db.session.commit()

    flash(f'{drive.job_title} has been deleted.', 'success')
    return redirect(url_for('admin.drives'))

@admin.route('/applications')
@login_required
@admin_required
def applications():
    """View all applications"""
    page = request.args.get('page', 1, type=int)
    applications = Application.query.order_by(Application.application_date.desc()).paginate(
        page=page, per_page=10
    )
    return render_template('admin/applications.html', applications=applications)
