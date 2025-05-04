import os
import sys
import random
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_backend.settings')
django.setup()

from core.models import Student, Classroom, Institute

def assign_random_categories(institute_id=None):
    """
    Assign random categories to students that don't have them.
    
    Args:
        institute_id: Optional ID of the institute to filter by
    """
    categories = ['junior_scholars', 'rising_intellects', 'mastermind_elite']
    
    # Base query for students
    base_query = Student.objects
    
    # Apply institute filter if provided
    if institute_id:
        try:
            institute = Institute.objects.get(id=institute_id)
            print(f"Filtering for institute: {institute.name} (ID: {institute_id})")
            base_query = base_query.filter(institute_id=institute_id)
        except Institute.DoesNotExist:
            print(f"Institute with ID {institute_id} does not exist")
            return
    
    # Find students with empty categories
    students_empty = base_query.filter(student_category='')
    print(f"Found {students_empty.count()} students with empty categories.")
    
    # Find students with null categories
    students_null = base_query.filter(student_category__isnull=True)
    print(f"Found {students_null.count()} students with null categories.")
    
    total = students_empty.count() + students_null.count()
    
    if total == 0:
        print("No students need category assignment.")
        
    # Process empty string categories
    for i, student in enumerate(students_empty):
        student.student_category = random.choice(categories)
        student.save()
        if i % 20 == 0:  # Show progress every 20 students
            print(f"Processed {i+1}/{students_empty.count()} students with empty categories...")
    
    # Process null categories
    for i, student in enumerate(students_null):
        student.student_category = random.choice(categories)
        student.save()
        if i % 20 == 0:  # Show progress every 20 students
            print(f"Processed {i+1}/{students_null.count()} students with null categories...")
    
    if total > 0:
        print("Finished assigning categories.")
    
    # Print some stats - filtered by institute if specified
    query = base_query
    
    junior_scholars = query.filter(student_category='junior_scholars').count()
    rising_intellects = query.filter(student_category='rising_intellects').count()
    mastermind_elite = query.filter(student_category='mastermind_elite').count()
    
    print(f"Student categories:")
    print(f"- Junior Scholars: {junior_scholars}")
    print(f"- Rising Intellects: {rising_intellects}")
    print(f"- Mastermind Elite: {mastermind_elite}")
    print(f"- Total: {junior_scholars + rising_intellects + mastermind_elite}")

if __name__ == "__main__":
    print("Updating student categories...")
    
    # Check if an institute ID was provided
    institute_id = None
    if len(sys.argv) > 1:
        try:
            institute_id = int(sys.argv[1])
            print(f"Using institute ID: {institute_id}")
        except ValueError:
            print(f"Invalid institute ID: {sys.argv[1]}")
            sys.exit(1)
    
    assign_random_categories(institute_id)
    print("Done!") 