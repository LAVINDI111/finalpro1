"""
Database setup script for ACNSMS
Run this script to create the database tables and insert sample data
"""

from app import app, db, User, Module, Schedule, StudentModule, Notification
from datetime import datetime, date, time, timedelta
import sys

def create_tables():
    """Create all database tables"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating tables: {str(e)}")
        return False
    return True

def create_sample_users():
    """Create sample users for testing"""
    try:
        with app.app_context():
            # Check if users already exist
            if User.query.first():
                print("✓ Users already exist, skipping creation")
                return True
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@acnsms.com',
                phone='+1234567890',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create lecturer users
            lecturer1 = User(
                username='lecturer1',
                email='lecturer1@acnsms.com',
                phone='+1234567891',
                role='lecturer'
            )
            lecturer1.set_password('lecturer123')
            db.session.add(lecturer1)
            
            lecturer2 = User(
                username='lecturer2',
                email='lecturer2@acnsms.com',
                phone='+1234567892',
                role='lecturer'
            )
            lecturer2.set_password('lecturer123')
            db.session.add(lecturer2)
            
            # Create student users
            for i in range(1, 6):
                student = User(
                    username=f'student{i}',
                    email=f'student{i}@acnsms.com',
                    phone=f'+123456789{i+2}',
                    role='student'
                )
                student.set_password('student123')
                db.session.add(student)
            
            db.session.commit()
            print("✓ Sample users created successfully")
    except Exception as e:
        print(f"✗ Error creating users: {str(e)}")
        return False
    return True

def create_sample_modules():
    """Create sample modules"""
    try:
        with app.app_context():
            # Check if modules already exist
            if Module.query.first():
                print("✓ Modules already exist, skipping creation")
                return True
            
            # Get lecturers
            lecturer1 = User.query.filter_by(username='lecturer1').first()
            lecturer2 = User.query.filter_by(username='lecturer2').first()
            
            if not lecturer1 or not lecturer2:
                print("✗ Lecturers not found, please create users first")
                return False
            
            # Create modules
            modules_data = [
                {
                    'module_code': 'CS101',
                    'module_name': 'Introduction to Computer Science',
                    'lecturer_id': lecturer1.id,
                    'credits': 3,
                    'description': 'Basic concepts of computer science and programming'
                },
                {
                    'module_code': 'MATH201',
                    'module_name': 'Calculus I',
                    'lecturer_id': lecturer2.id,
                    'credits': 4,
                    'description': 'Differential and integral calculus'
                },
                {
                    'module_code': 'ENG101',
                    'module_name': 'English Composition',
                    'lecturer_id': lecturer1.id,
                    'credits': 3,
                    'description': 'Academic writing and communication skills'
                },
                {
                    'module_code': 'PHYS101',
                    'module_name': 'Physics I',
                    'lecturer_id': lecturer2.id,
                    'credits': 4,
                    'description': 'Mechanics and thermodynamics'
                }
            ]
            
            for module_data in modules_data:
                module = Module(**module_data)
                db.session.add(module)
            
            db.session.commit()
            print("✓ Sample modules created successfully")
    except Exception as e:
        print(f"✗ Error creating modules: {str(e)}")
        return False
    return True

def create_student_enrollments():
    """Enroll students in modules"""
    try:
        with app.app_context():
            # Check if enrollments already exist
            if StudentModule.query.first():
                print("✓ Student enrollments already exist, skipping creation")
                return True
            
            # Get students and modules
            students = User.query.filter_by(role='student').all()
            modules = Module.query.all()
            
            # Enroll each student in random modules
            for student in students:
                # Enroll in first 2-3 modules
                for i, module in enumerate(modules[:3]):
                    if i < 2 or (i == 2 and student.id % 2 == 0):  # Some variety
                        enrollment = StudentModule(
                            student_id=student.id,
                            module_id=module.id
                        )
                        db.session.add(enrollment)
            
            db.session.commit()
            print("✓ Student enrollments created successfully")
    except Exception as e:
        print(f"✗ Error creating enrollments: {str(e)}")
        return False
    return True

def create_sample_schedules():
    """Create sample schedules"""
    try:
        with app.app_context():
            # Check if schedules already exist
            if Schedule.query.first():
                print("✓ Schedules already exist, skipping creation")
                return True
            
            # Get modules
            modules = Module.query.all()
            
            # Create schedules for the next few weeks
            base_date = date.today()
            
            schedule_data = [
                # CS101 schedules
                {
                    'module_id': modules[0].id,
                    'classroom': 'Room 101',
                    'date': base_date,
                    'start_time': time(9, 0),
                    'end_time': time(10, 30)
                },
                {
                    'module_id': modules[0].id,
                    'classroom': 'Room 101',
                    'date': base_date + timedelta(days=7),
                    'start_time': time(14, 0),
                    'end_time': time(15, 30)
                },
                # MATH201 schedules
                {
                    'module_id': modules[1].id,
                    'classroom': 'Room 201',
                    'date': base_date,
                    'start_time': time(11, 0),
                    'end_time': time(12, 30)
                },
                {
                    'module_id': modules[1].id,
                    'classroom': 'Room 201',
                    'date': date(base_date.year, base_date.month, base_date.day + 1),
                    'start_time': time(10, 0),
                    'end_time': time(11, 30)
                },
                # ENG101 schedules
                {
                    'module_id': modules[2].id,
                    'classroom': 'Room 301',
                    'date': date(base_date.year, base_date.month, base_date.day + 1),
                    'start_time': time(14, 0),
                    'end_time': time(15, 30)
                },
                # PHYS101 schedules
                {
                    'module_id': modules[3].id,
                    'classroom': 'Lab 101',
                    'date': date(base_date.year, base_date.month, base_date.day + 3),
                    'start_time': time(9, 0),
                    'end_time': time(11, 0)
                }
            ]
            
            for schedule_info in schedule_data:
                schedule = Schedule(**schedule_info)
                db.session.add(schedule)
            
            db.session.commit()
            print("✓ Sample schedules created successfully")
    except Exception as e:
        print(f"✗ Error creating schedules: {str(e)}")
        return False
    return True

def setup_database():
    """Complete database setup"""
    print("Setting up ACNSMS database...")
    print("=" * 50)
    
    # Create tables
    if not create_tables():
        return False
    
    # Create sample data
    if not create_sample_users():
        return False
    
    if not create_sample_modules():
        return False
    
    if not create_student_enrollments():
        return False
    
    if not create_sample_schedules():
        return False
    
    print("=" * 50)
    print("✓ Database setup completed successfully!")
    print("\nSample login credentials:")
    print("Admin: admin / admin123")
    print("Lecturer: lecturer1 / lecturer123")
    print("Student: student1 / student123")
    print("\nYou can now run the application with: python app.py")
    
    return True

if __name__ == '__main__':
    try:
        setup_database()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1)