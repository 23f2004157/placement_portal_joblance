# Placement Portal Application

A web-based placement portal application for managing campus recruitment activities involving companies, students, and placement drives.

## Tech Stack
- Backend: Flask
- Frontend: Jinja2 templating, HTML, CSS, Bootstrap
- Database: SQLite
- Authentication: Flask-Login
- Forms: Flask-WTF

## Features
- Role-based access for Admin, Company, and Student
- Admin can approve/reject companies and placement drives
- Companies can create placement drives and manage applications
- Students can apply for placement drives and track application status
- Complete application history and statistics

## Installation
1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   python app.py
   ```
   The admin user will be created automatically.

5. Run the application:
   ```
   python app.py
   ```

6. Access the application at:
   ```
   http://127.0.0.1:5000/
   ```

## Default Admin Credentials
- Username: admin
- Password: admin123

## Project Structure
```
placement_portal/
├── app.py                 # Main application file
├── config.py              # Application configuration
├── requirements.txt       # Python dependencies
├── models.py              # Database models
├── forms.py               # WTForms for form handling
├── auth.py                # Authentication routes
├── admin.py               # Admin routes
├── company.py             # Company routes
├── student.py             # Student routes
├── templates/             # Jinja2 templates
│   ├── base.html          # Base template
│   ├── auth/              # Authentication templates
│   ├── admin/             # Admin templates
│   ├── company/           # Company templates
│   └── student/           # Student templates
├── static/                # Static files
│   ├── css/               # Custom CSS
│   ├── js/                # Custom JavaScript
│   └── uploads/           # User uploads (resumes, etc.)
└── instance/              # Instance folder for SQLite database
```
