"""
ACNSMS - Automated Campus Notification and Schedule Management System
Main Flask application file
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/acnsms')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import notification services
from services.notification_service import NotificationService
from services.calendar_service import CalendarService

# Initialize services
notification_service = NotificationService()
calendar_service = CalendarService()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Models
class User(UserMixin, db.Model):
    """User model for authentication and role management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # student, lecturer, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

class Module(db.Model):
    """Module/Course model"""
    id = db.Column(db.Integer, primary_key=True)
    module_code = db.Column(db.String(20), unique=True, nullable=False)
    module_name = db.Column(db.String(100), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    credits = db.Column(db.Integer, default=3)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    lecturer = db.relationship('User', backref='modules_taught')
    schedules = db.relationship('Schedule', backref='module', lazy=True)

class Schedule(db.Model):
    """Schedule/Timetable model"""
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    classroom = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, rescheduled, cancelled
    google_event_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    notifications = db.relationship('Notification', backref='schedule', lazy=True)

class Notification(db.Model):
    """Notification tracking model"""
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)  # email, sms
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='notifications')

class StudentModule(db.Model):
    """Many-to-many relationship between students and modules"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('User', backref='enrolled_modules')
    module = db.relationship('Module', backref='enrolled_students')

# Routes
@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        role = request.form['role']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email, phone=phone, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if current_user.role == 'student':
        # Get student's enrolled modules and their schedules
        enrolled_modules = db.session.query(Module).join(StudentModule).filter(
            StudentModule.student_id == current_user.id
        ).all()
        
        schedules = []
        for module in enrolled_modules:
            module_schedules = Schedule.query.filter_by(module_id=module.id).all()
            schedules.extend(module_schedules)
        
        return render_template('dashboard_student.html', schedules=schedules, modules=enrolled_modules)
    
    elif current_user.role == 'lecturer':
        # Get lecturer's modules and schedules
        modules = Module.query.filter_by(lecturer_id=current_user.id).all()
        schedules = []
        for module in modules:
            module_schedules = Schedule.query.filter_by(module_id=module.id).all()
            schedules.extend(module_schedules)
        
        return render_template('dashboard_lecturer.html', schedules=schedules, modules=modules)
    
    elif current_user.role == 'admin':
        # Get all modules and schedules for admin
        modules = Module.query.all()
        schedules = Schedule.query.all()
        users = User.query.all()
        
        return render_template('dashboard_admin.html', schedules=schedules, modules=modules, users=users)

@app.route('/schedule/create', methods=['GET', 'POST'])
@login_required
def create_schedule():
    """Create new schedule"""
    if current_user.role not in ['lecturer', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        module_id = request.form['module_id']
        classroom = request.form['classroom']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        
        # Create schedule
        schedule = Schedule(
            module_id=module_id,
            classroom=classroom,
            date=date,
            start_time=start_time,
            end_time=end_time
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        # Add to Google Calendar
        try:
            module = Module.query.get(module_id)
            event_id = calendar_service.create_event(
                title=f"{module.module_code} - {module.module_name}",
                location=classroom,
                start_datetime=datetime.combine(date, start_time),
                end_datetime=datetime.combine(date, end_time),
                description=f"Lecturer: {module.lecturer.username}"
            )
            
            schedule.google_event_id = event_id
            db.session.commit()
            
            flash('Schedule created successfully and added to calendar!', 'success')
        except Exception as e:
            flash(f'Schedule created but calendar sync failed: {str(e)}', 'warning')
        
        return redirect(url_for('dashboard'))
    
    # Get modules for the form
    if current_user.role == 'lecturer':
        modules = Module.query.filter_by(lecturer_id=current_user.id).all()
    else:
        modules = Module.query.all()
    
    return render_template('create_schedule.html', modules=modules)

@app.route('/schedule/reschedule/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
def reschedule(schedule_id):
    """Reschedule a lecture"""
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Check permissions
    if current_user.role == 'lecturer' and schedule.module.lecturer_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    elif current_user.role not in ['lecturer', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        new_classroom = request.form['classroom']
        new_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        new_start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        new_end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        
        # Store old values for notification
        old_date = schedule.date
        old_classroom = schedule.classroom
        old_start_time = schedule.start_time
        
        # Update schedule
        schedule.classroom = new_classroom
        schedule.date = new_date
        schedule.start_time = new_start_time
        schedule.end_time = new_end_time
        schedule.status = 'rescheduled'
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Update Google Calendar event
        try:
            if schedule.google_event_id:
                calendar_service.update_event(
                    event_id=schedule.google_event_id,
                    title=f"{schedule.module.module_code} - {schedule.module.module_name}",
                    location=new_classroom,
                    start_datetime=datetime.combine(new_date, new_start_time),
                    end_datetime=datetime.combine(new_date, new_end_time)
                )
        except Exception as e:
            flash(f'Calendar update failed: {str(e)}', 'warning')
        
        # Send notifications to students and admin
        try:
            send_reschedule_notifications(schedule, old_date, old_classroom, old_start_time)
            flash('Schedule rescheduled successfully and notifications sent!', 'success')
        except Exception as e:
            flash(f'Schedule rescheduled but notifications failed: {str(e)}', 'warning')
        
        return redirect(url_for('dashboard'))
    
    return render_template('reschedule.html', schedule=schedule)

def send_reschedule_notifications(schedule, old_date, old_classroom, old_start_time):
    """Send email and SMS notifications for rescheduled lectures"""
    module = schedule.module
    
    # Prepare notification message
    message = f"""
    LECTURE RESCHEDULED
    
    Module: {module.module_code} - {module.module_name}
    Lecturer: {module.lecturer.username}
    
    OLD SCHEDULE:
    Date: {old_date.strftime('%Y-%m-%d')}
    Time: {old_start_time.strftime('%H:%M')}
    Room: {old_classroom}
    
    NEW SCHEDULE:
    Date: {schedule.date.strftime('%Y-%m-%d')}
    Time: {schedule.start_time.strftime('%H:%M')}
    Room: {schedule.classroom}
    
    Please update your schedule accordingly.
    """
    
    # SMS message (shorter version)
    sms_message = f"ACNSMS: {module.module_code} rescheduled to {schedule.date.strftime('%Y-%m-%d')} {schedule.start_time.strftime('%H:%M')} in {schedule.classroom}. Lecturer: {module.lecturer.username}"
    
    # Get all students enrolled in this module
    students = db.session.query(User).join(StudentModule).filter(
        StudentModule.module_id == module.id
    ).all()
    
    # Get admin users
    admins = User.query.filter_by(role='admin').all()
    
    # Combine all recipients
    recipients = students + admins
    
    # Send notifications
    for user in recipients:
        # Send email
        if user.email:
            try:
                notification_service.send_email(
                    to_email=user.email,
                    subject=f"Lecture Rescheduled: {module.module_code}",
                    message=message
                )
                
                # Log notification
                notification = Notification(
                    schedule_id=schedule.id,
                    user_id=user.id,
                    notification_type='email',
                    status='sent',
                    message=message,
                    sent_at=datetime.utcnow()
                )
                db.session.add(notification)
            except Exception as e:
                print(f"Failed to send email to {user.email}: {str(e)}")
        
        # Send SMS
        if user.phone:
            try:
                notification_service.send_sms(
                    to_phone=user.phone,
                    message=sms_message
                )
                
                # Log notification
                notification = Notification(
                    schedule_id=schedule.id,
                    user_id=user.id,
                    notification_type='sms',
                    status='sent',
                    message=sms_message,
                    sent_at=datetime.utcnow()
                )
                db.session.add(notification)
            except Exception as e:
                print(f"Failed to send SMS to {user.phone}: {str(e)}")
    
    db.session.commit()

@app.route('/api/schedules')
@login_required
def api_schedules():
    """API endpoint to get schedules as JSON"""
    schedules = Schedule.query.all()
    schedule_list = []
    
    for schedule in schedules:
        schedule_data = {
            'id': schedule.id,
            'title': f"{schedule.module.module_code} - {schedule.module.module_name}",
            'start': f"{schedule.date}T{schedule.start_time}",
            'end': f"{schedule.date}T{schedule.end_time}",
            'classroom': schedule.classroom,
            'lecturer': schedule.module.lecturer.username,
            'status': schedule.status
        }
        schedule_list.append(schedule_data)
    
    return jsonify(schedule_list)

# Initialize database
@app.before_first_request
def create_tables():
    """Create database tables"""
    db.create_all()
    
    # Create default admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@acnsms.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)