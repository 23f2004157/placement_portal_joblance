from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateField, FloatField, IntegerField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from models import User, Student, Company

class LoginForm(FlaskForm):
    """Login form for all user types"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Base registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('User Type', choices=[('company', 'Company'), ('student', 'Student')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class CompanyProfileForm(FlaskForm):
    """Form for company profile"""
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    hr_contact = StringField('HR Contact Name', validators=[DataRequired(), Length(max=100)])
    hr_email = StringField('HR Email', validators=[DataRequired(), Email()])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    description = TextAreaField('Company Description', validators=[Optional()])
    submit = SubmitField('Submit')

class StudentProfileForm(FlaskForm):
    """Form for student profile"""
    student_id = StringField('Student ID', validators=[DataRequired(), Length(max=20)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    department = SelectField('Department', choices=[
        ('Computer Science', 'Computer Science'),
        ('Information Technology', 'Information Technology'),
        ('Electronics', 'Electronics'),
        ('Electrical', 'Electrical'),
        ('Mechanical', 'Mechanical'),
        ('Civil', 'Civil'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    year = SelectField('Year', choices=[
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year')
    ], validators=[DataRequired()], coerce=int)
    cgpa = FloatField('CGPA', validators=[DataRequired()])
    skills = TextAreaField('Skills (comma-separated)', validators=[Optional()])
    resume = FileField('Resume', validators=[Optional()])
    submit = SubmitField('Submit')

class PlacementDriveForm(FlaskForm):
    """Form for creating placement drives"""
    job_title = StringField('Job Title', validators=[DataRequired(), Length(max=100)])
    job_description = TextAreaField('Job Description', validators=[DataRequired()])
    eligibility_criteria = TextAreaField('Eligibility Criteria', validators=[DataRequired()])
    application_deadline = DateField('Application Deadline', validators=[DataRequired()], format='%Y-%m-%d')
    salary_package = StringField('Salary Package', validators=[Optional(), Length(max=50)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Submit')

class ApplicationStatusForm(FlaskForm):
    """Form for updating application status"""
    status = SelectField('Status', choices=[
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Update Status')

class SearchForm(FlaskForm):
    """Form for searching students and companies"""
    search_term = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
