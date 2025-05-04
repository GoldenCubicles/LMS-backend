import os
import sys
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_backend.settings')
django.setup()

from core.models import Teacher

def check_teacher(email=None):
    """
    Check teacher information in the database.
    
    If email is provided, check for a specific teacher, otherwise list all teachers.
    """
    if email:
        try:
            teacher = Teacher.objects.get(email=email)
            print(f"Found teacher: {teacher.name} (ID: {teacher.id})")
            print(f"Email: {teacher.email}")
            print(f"Password: {teacher.password}")
            print(f"Institute: {teacher.institute.name if teacher.institute else 'None'}")
            print(f"Active: {teacher.is_active}")
            return teacher
        except Teacher.DoesNotExist:
            print(f"No teacher found with email: {email}")
            return None
    else:
        teachers = Teacher.objects.all()
        print(f"Found {teachers.count()} teacher(s):")
        for i, teacher in enumerate(teachers, 1):
            print(f"{i}. {teacher.name} - {teacher.email} - Password: {teacher.password}")
        return teachers

def update_teacher_password(email, new_password):
    """
    Update a teacher's password in the database.
    """
    try:
        teacher = Teacher.objects.get(email=email)
        old_password = teacher.password
        teacher.password = new_password
        teacher.save()
        
        print(f"Updated password for teacher: {teacher.name}")
        print(f"Old password: {old_password}")
        print(f"New password: {new_password}")
        return True
    except Teacher.DoesNotExist:
        print(f"No teacher found with email: {email}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python check_and_update_teacher.py check [email]")
        print("  python check_and_update_teacher.py update <email> <new_password>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        email = sys.argv[2] if len(sys.argv) > 2 else None
        check_teacher(email)
    
    elif command == "update":
        if len(sys.argv) != 4:
            print("Usage for update: python check_and_update_teacher.py update <email> <new_password>")
            sys.exit(1)
        
        email = sys.argv[2]
        new_password = sys.argv[3]
        update_teacher_password(email, new_password)
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: check, update")
        sys.exit(1) 