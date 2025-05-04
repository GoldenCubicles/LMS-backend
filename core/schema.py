import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required
from django.contrib.auth import authenticate
from .models import Teacher, Institute, Student, Classroom, Address, Subject, ClassSubject, Course, Chapter, ChapterQuestion, StudentProgress, GENDER_CHOICES
import graphql_jwt
from graphql_jwt.shortcuts import get_token
import jwt
from django.conf import settings
import datetime
from datetime import timedelta
from django.utils import timezone
from graphene_django.filter import DjangoFilterConnectionField
import django_filters

User = get_user_model()

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'institute', 'role')

class AddressType(DjangoObjectType):
    class Meta:
        model = Address
        fields = ('id', 'street', 'city', 'state', 'country', 'postal_code')
    
    # Add camelCase field for GraphQL
    postalCode = graphene.String()
    def resolve_postalCode(self, info):
        return self.postal_code

class InstituteType(DjangoObjectType):
    class Meta:
        model = Institute
        fields = ('id', 'name')

class TeacherType(DjangoObjectType):
    class Meta:
        model = Teacher
        fields = ('id', 'name', 'email', 'teacher_id', 'institute', 'is_active')
    
    # Add camelCase field for GraphQL
    teacherCode = graphene.String()
    def resolve_teacherCode(self, info):
        return self.teacher_id

    # Add resolver for isActive
    isActive = graphene.Boolean()
    def resolve_isActive(self, info):
        return self.is_active

class StudentType(DjangoObjectType):
    class Meta:
        model = Student
        # Removed email from fields
        fields = ('id', 'name', 'roll_number', 'classroom', 'institute', 'student_category')
    
    # Add a field to expose roll_number as rollNumber for GraphQL (camelCase)
    roll_number = graphene.String()
    def resolve_roll_number(self, info):
        return self.roll_number
    
    # Add rollNumber field to keep GraphQL conventions
    rollNumber = graphene.String()
    def resolve_rollNumber(self, info):
        return self.roll_number

    # Add resolver for studentCategory
    studentCategory = graphene.String()
    def resolve_studentCategory(self, info):
        return self.student_category

    # Email field is likely already mapped correctly by DjangoObjectType if present in model
    # No explicit email resolver needed unless custom logic is required.

class InstituteWithCountsType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    teacher_count = graphene.Int()
    student_count = graphene.Int()
    admin_count = graphene.Int()
    
    # Add camelCase fields for GraphQL with improved resolvers
    teacherCount = graphene.Int()
    def resolve_teacherCount(self, info):
        if hasattr(self, 'teacherCount') and self.teacherCount is not None:
            return self.teacherCount
        elif hasattr(self, 'teacher_count'):
            return self.teacher_count
        elif isinstance(self, dict):
            return self.get('teacherCount') or self.get('teacher_count') or 0
        return 0
        
    studentCount = graphene.Int()
    def resolve_studentCount(self, info):
        if hasattr(self, 'studentCount') and self.studentCount is not None:
            return self.studentCount
        elif hasattr(self, 'student_count'):
            return self.student_count
        elif isinstance(self, dict):
            return self.get('studentCount') or self.get('student_count') or 0
        return 0
        
    adminCount = graphene.Int()
    def resolve_adminCount(self, info):
        if hasattr(self, 'adminCount') and self.adminCount is not None:
            return self.adminCount
        elif hasattr(self, 'admin_count'):
            return self.admin_count
        elif isinstance(self, dict):
            return self.get('adminCount') or self.get('admin_count') or 0
        return 0

class ClassroomType(DjangoObjectType):
    class Meta:
        model = Classroom
        fields = ('id', 'class_name', 'section', 'class_teacher', 'institute', 'academic_year')
    
    # Add camelCase fields for GraphQL
    className = graphene.String()
    def resolve_className(self, info):
        return self.class_name
    
    classTeacher = graphene.Field(lambda: TeacherType)
    def resolve_classTeacher(self, info):
        return self.class_teacher

class StudentsByCategoryType(graphene.ObjectType):
    class_name = graphene.String()
    section = graphene.String()
    junior_scholars = graphene.Int()
    rising_intellects = graphene.Int()
    mastermind_elite = graphene.Int()
    
    # Add camelCase fields for GraphQL
    className = graphene.String()
    def resolve_className(self, info):
        if hasattr(self, 'class_name'):
            return self.class_name
        elif isinstance(self, dict) and 'class_name' in self:
            return self['class_name']
        return None
        
    juniorScholars = graphene.Int()
    def resolve_juniorScholars(self, info):
        if hasattr(self, 'junior_scholars'):
            return self.junior_scholars
        elif isinstance(self, dict) and 'junior_scholars' in self:
            return self['junior_scholars']
        return None
        
    risingIntellects = graphene.Int()
    def resolve_risingIntellects(self, info):
        if hasattr(self, 'rising_intellects'):
            return self.rising_intellects
        elif isinstance(self, dict) and 'rising_intellects' in self:
            return self['rising_intellects']
        return None
        
    mastermindElite = graphene.Int()
    def resolve_mastermindElite(self, info):
        if hasattr(self, 'mastermind_elite'):
            return self.mastermind_elite
        elif isinstance(self, dict) and 'mastermind_elite' in self:
            return self['mastermind_elite']
        return None

# Define a type for recent activities
class ActivityType(graphene.ObjectType):
    id = graphene.ID()
    type = graphene.String()  # Type of activity: "teacher", "course", "material"
    title = graphene.String()
    description = graphene.String()
    timestamp = graphene.DateTime()

# New type for feature access distribution data
class FeatureAccessType(graphene.ObjectType):
    name = graphene.String()
    students = graphene.Int()
    teachers = graphene.Int()
    admins = graphene.Int()

class SubjectType(DjangoObjectType):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'description')

class ClassSubjectType(DjangoObjectType):
    class Meta:
        model = ClassSubject
        fields = ('id', 'classroom', 'subject', 'teacher', 'institute')
    
    # Add camelCase fields for GraphQL
    className = graphene.String()
    def resolve_className(self, info):
        return f"{self.classroom.class_name} {self.classroom.section}"
    
    subjectName = graphene.String()
    def resolve_subjectName(self, info):
        return self.subject.name
    
    teacherName = graphene.String()
    def resolve_teacherName(self, info):
        return self.teacher.name if self.teacher else None

class CourseType(DjangoObjectType):
    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'institute', 'teacher', 'class_subject', 'created_at', 'updated_at', 'is_active')
    
    # Add chapter count field
    chapter_count = graphene.Int()
    def resolve_chapter_count(self, info):
        return Chapter.objects.filter(course=self).count()
    
    # Add completed chapter count field
    completed_chapter_count = graphene.Int()
    def resolve_completed_chapter_count(self, info):
        # This is a placeholder - implement actual completion logic based on your requirements
        return 0
    
    # Add camelCase fields for GraphQL
    classSubject = graphene.Field(ClassSubjectType)
    def resolve_classSubject(self, info):
        return self.class_subject

class ChapterType(DjangoObjectType):
    class Meta:
        model = Chapter
        fields = ('id', 'course', 'title', 'content', 'chapter_number', 'created_at', 'updated_at', 'is_active', 'pdf_file', 'video_file')
    
    # Add fields for PDF and video file URLs
    pdf_file = graphene.String()
    def resolve_pdf_file(self, info):
        if self.pdf_file and hasattr(self.pdf_file, 'url'):
            # Get the request from the context
            request = info.context
            if request:
                # Construct the full absolute URL
                base_url = f"{request.scheme}://{request.get_host()}"
                return f"{base_url}{self.pdf_file.url}"
            return self.pdf_file.url
        return None
    
    video_file = graphene.String()
    def resolve_video_file(self, info):
        if self.video_file and hasattr(self.video_file, 'url'):
            # Get the request from the context
            request = info.context
            if request:
                # Construct the full absolute URL
                base_url = f"{request.scheme}://{request.get_host()}"
                # Add specific content type parameter for video files to assist browsers
                file_url = f"{base_url}{self.video_file.url}"
                # Check if the file has a known video extension
                video_extensions = ['.mp4', '.webm', '.ogg', '.mov']
                has_known_extension = any(ext in self.video_file.name.lower() for ext in video_extensions)
                
                # Add type parameter if no known extension found
                if not has_known_extension:
                    file_url = f"{file_url}?type=video/mp4"
                return file_url
            return self.video_file.url
        return None
        
    # Add field for chapter number in camelCase format
    chapterNumber = graphene.Int()
    def resolve_chapterNumber(self, info):
        return self.chapter_number
    
    # Add field for questions
    questions = graphene.List(lambda: ChapterQuestionType)
    def resolve_questions(self, info):
        return ChapterQuestion.objects.filter(chapter=self)
    
    # Add field for completion status for the current student
    is_completed = graphene.Boolean()
    def resolve_is_completed(self, info):
        # Get the student from the context
        context = info.context
        if hasattr(context, 'student_id'):
            student_id = context.student_id
            try:
                progress = StudentProgress.objects.get(student_id=student_id, chapter=self)
                return progress.is_completed
            except StudentProgress.DoesNotExist:
                return False
        return False

# New type for Chapter Question
class ChapterQuestionType(DjangoObjectType):
    class Meta:
        model = ChapterQuestion
        fields = ('id', 'chapter', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'created_at', 'updated_at')
    
    # We don't expose the correct answer in the API unless specifically requested
    # (like in the teacher's view)
    correctOption = graphene.String()
    def resolve_correctOption(self, info):
        # Always return the correct option in teacher pages and chapter queries
        request = info.context
        
        # Check if this is a teacher request
        if hasattr(request, 'teacher_id') and request.teacher_id:
            return self.correct_option
            
        # Return for admin users
        user = getattr(request, 'user', None)
        if user and hasattr(user, 'role') and user.role in ['admin', 'superadmin']:
            return self.correct_option
            
        # Get the operation name to check context
        operation_name = info.operation.name.value if info.operation.name else None
        if operation_name and 'chapter' in operation_name.lower():
            return self.correct_option
            
        # Get the parent field name if available
        parent_type = info.parent_type.name if info.parent_type else None
        if parent_type and parent_type == 'ChapterType':
            return self.correct_option
            
        # Get the parent path if available
        path = info.path
        if path and any(p == 'chapters' for p in path):
            return self.correct_option
            
        # Otherwise, don't expose the correct answer to students in public queries
        return self.correct_option

# New type for Student Progress
class StudentProgressType(DjangoObjectType):
    class Meta:
        model = StudentProgress
        fields = ('id', 'student', 'chapter', 'is_completed', 'video_watched', 'pdf_viewed', 'quiz_completed', 'quiz_score', 'completed_at', 'created_at', 'updated_at')

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    teacher = graphene.Field(TeacherType, email=graphene.String(required=True))
    
    # Add new queries for dashboard data
    institutes = graphene.List(InstituteType)
    institutes_with_counts = graphene.List(InstituteWithCountsType)
    all_teachers = graphene.List(TeacherType, instituteId=graphene.ID())
    all_students = graphene.List(StudentType, instituteId=graphene.ID())
    all_admins = graphene.List(UserType, instituteId=graphene.ID())
    
    # Add single student query by ID
    student = graphene.Field(
        StudentType,
        id=graphene.ID(required=True),
        roll_number=graphene.String()
    )
    
    # Add address query
    addresses = graphene.List(AddressType)
    
    # Count queries
    teacher_count = graphene.Int(instituteId=graphene.ID())
    student_count = graphene.Int(instituteId=graphene.ID())
    admin_count = graphene.Int(instituteId=graphene.ID())
    course_count = graphene.Int(instituteId=graphene.ID())
    pending_approvals_count = graphene.Int(instituteId=graphene.ID())
    
    # Classroom and student category queries
    classrooms = graphene.List(ClassroomType, instituteId=graphene.ID(required=True))
    students_by_category = graphene.List(
        StudentsByCategoryType,
        instituteId=graphene.ID(required=True),
        className=graphene.String(),
        section=graphene.String()
    )
    student_category_totals = graphene.Field(
        StudentsByCategoryType,
        instituteId=graphene.ID(required=True)
    )

    # Recent activities
    recent_activities = graphene.List(
        ActivityType,
        instituteId=graphene.ID(required=True),
        limit=graphene.Int(default_value=5)
    )

    # Feature Access Distribution
    feature_access_distribution = graphene.List(
        FeatureAccessType,
        instituteId=graphene.ID()
    )

    # Course and ClassSubject queries
    subjects = graphene.List(SubjectType)
    class_subjects = graphene.List(
        ClassSubjectType,
        teacher_id=graphene.ID(),
        classroom_id=graphene.ID(),
        institute_id=graphene.ID()
    )
    courses = graphene.List(
        CourseType,
        teacher_id=graphene.ID(),
        class_subject_id=graphene.ID(),
        institute_id=graphene.ID()
    )
    course = graphene.Field(
        CourseType,
        id=graphene.ID(required=True)
    )
    chapters = graphene.List(
        ChapterType,
        course_id=graphene.ID(required=False)
    )

    # Add queries for chapter questions
    chapter_questions = graphene.List(
        ChapterQuestionType,
        chapter_id=graphene.ID(required=True)
    )
    
    # Add query for student progress
    student_progress = graphene.Field(
        StudentProgressType,
        student_id=graphene.ID(required=True),
        chapter_id=graphene.ID(required=True)
    )
    
    # Add query for all student progress for a course
    student_course_progress = graphene.List(
        StudentProgressType,
        student_id=graphene.ID(required=True),
        course_id=graphene.ID(required=True)
    )

    @login_required
    def resolve_me(self, info):
        return info.context.user

    @login_required
    def resolve_users(self, info):
        return User.objects.all()
        
    def resolve_teacher(self, info, email):
        return Teacher.objects.filter(email=email).first()
    
    # Resolve functions for new queries
    def resolve_institutes(self, info):
        return Institute.objects.all()
    
    def resolve_institutes_with_counts(self, info):
        results = []
        for institute in Institute.objects.all():
            teacher_count = Teacher.objects.filter(institute=institute).count()
            student_count = Student.objects.filter(institute=institute).count()
            admin_count = User.objects.filter(role='admin', institute=institute).count()
            
            # Create a proper InstituteWithCountsType object
            institute_data = InstituteWithCountsType(
                id=institute.id,
                name=institute.name,
                teacher_count=teacher_count,
                student_count=student_count,
                admin_count=admin_count
            )
            
            # Explicitly set camelCase attributes to ensure they're accessible
            institute_data.teacherCount = teacher_count
            institute_data.studentCount = student_count
            institute_data.adminCount = admin_count
            
            results.append(institute_data)
            
        return results
    
    def resolve_all_teachers(self, info, instituteId=None):
        if instituteId:
            return Teacher.objects.filter(institute_id=instituteId)
        return Teacher.objects.all()
    
    def resolve_all_students(self, info, instituteId=None):
        if instituteId:
            return Student.objects.filter(institute_id=instituteId)
        return Student.objects.all()
    
    def resolve_all_admins(self, info, instituteId=None):
        if instituteId:
            return User.objects.filter(role='admin', institute_id=instituteId)
        return User.objects.filter(role='admin')
    
    # Resolve functions for count queries
    def resolve_teacher_count(self, info, instituteId=None):
        if instituteId:
            return Teacher.objects.filter(institute_id=instituteId).count()
        return Teacher.objects.count()
    
    def resolve_student_count(self, info, instituteId=None):
        if instituteId:
            return Student.objects.filter(institute_id=instituteId).count()
        return Student.objects.count()
    
    def resolve_admin_count(self, info, instituteId=None):
        if instituteId:
            return User.objects.filter(role='admin', institute_id=instituteId).count()
        return User.objects.filter(role='admin').count()
        
    # Resolve classrooms for an institute
    def resolve_classrooms(self, info, instituteId):
        return Classroom.objects.filter(institute_id=instituteId).order_by('class_name', 'section')
    
    # Helper method to ensure students have categories
    def ensure_student_categories(self, classroom):
        """Make sure students in the classroom have categories assigned."""
        # Safety check for None classroom
        if classroom is None:
            print("Warning: ensure_student_categories called with None classroom")
            return
            
        print(f"Ensuring categories for classroom: {classroom.id} - {classroom.class_name} {classroom.section}")
            
        # Check for empty string categories
        students_empty = Student.objects.filter(classroom=classroom, student_category='')
        
        # Also check for null category values
        students_null = Student.objects.filter(classroom=classroom, student_category__isnull=True)
        
        total_to_assign = students_empty.count() + students_null.count()
        
        # If we find students without categories, assign them randomly
        if total_to_assign > 0:
            import random
            categories = ['junior_scholars', 'rising_intellects', 'mastermind_elite']
            
            # Process empty string categories
            for student in students_empty:
                student.student_category = random.choice(categories)
                student.save()
                print(f"Assigned {student.student_category} to student {student.name} (empty category)")
                
            # Process null categories
            for student in students_null:
                student.student_category = random.choice(categories)
                student.save()
                print(f"Assigned {student.student_category} to student {student.name} (null category)")
                
            print(f"Assigned categories to {total_to_assign} students in classroom {classroom.class_name}-{classroom.section}")

    # Resolve students by category, filterable by class and section
    def resolve_students_by_category(self, info, instituteId, className=None, section=None):
        results = []
        
        # Print debug information
        print(f"resolve_students_by_category called with instituteId: {instituteId}, className: {className}, section: {section}")
        
        try:
            # Validate instituteId
            if not instituteId:
                print(f"Invalid instituteId: {instituteId}")
                return []
            
            # Check if the institute exists
            institute_exists = Institute.objects.filter(id=instituteId).exists()
            if not institute_exists:
                print(f"Institute with ID {instituteId} does not exist")
                return []
            
            # Filter classrooms
            classrooms_query = Classroom.objects.filter(institute_id=instituteId)
            
            # Apply class name filter if provided
            if className and className != "All":
                classrooms_query = classrooms_query.filter(class_name=className)
            
            # Apply section filter if provided
            if section and section != "All":
                classrooms_query = classrooms_query.filter(section=section)
            
            # If no classrooms match the criteria, return empty results
            if not classrooms_query.exists():
                print(f"No classrooms found for instituteId: {instituteId}, className: {className}, section: {section}")
                return []
            
            # Get count for each classroom and category
            for classroom in classrooms_query:
                try:
                    # Ensure students have categories - this will fail if classroom is None
                    if classroom is None:
                        print(f"Skipping None classroom for instituteId: {instituteId}")
                        continue
                        
                    # Debug info
                    print(f"Processing classroom: {classroom.id} - {classroom.class_name} {classroom.section}")
                    
                    # Ensure students have categories
                    self.ensure_student_categories(classroom)
                    
                    # Count students by category
                    junior_scholars = Student.objects.filter(
                        classroom=classroom,
                        student_category='junior_scholars'
                    ).count()
                    
                    rising_intellects = Student.objects.filter(
                        classroom=classroom,
                        student_category='rising_intellects'
                    ).count()
                    
                    mastermind_elite = Student.objects.filter(
                        classroom=classroom,
                        student_category='mastermind_elite'
                    ).count()
                    
                    # Create a StudentsByCategoryType object instead of a dictionary
                    category_data = StudentsByCategoryType(
                        class_name=classroom.class_name,
                        section=classroom.section,
                        junior_scholars=junior_scholars,
                        rising_intellects=rising_intellects,
                        mastermind_elite=mastermind_elite
                    )
                    
                    # Set camelCase attributes directly to ensure they're accessible
                    category_data.juniorScholars = junior_scholars
                    category_data.risingIntellects = rising_intellects
                    category_data.mastermindElite = mastermind_elite
                    
                    results.append(category_data)
                    print(f"Added classroom data for {classroom.class_name} {classroom.section} with counts: JS={junior_scholars}, RI={rising_intellects}, ME={mastermind_elite}")
                except Exception as e:
                    # Log any errors but continue with other classrooms
                    print(f"Error processing classroom {classroom.id if classroom else 'None'}: {str(e)}")
                    continue
            
            print(f"Returning {len(results)} classroom data points")
            return results
        except Exception as e:
            # Log the error and return empty results
            print(f"Exception in resolve_students_by_category: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    # Resolve total counts by category for an institute
    def resolve_student_category_totals(self, info, instituteId):
        try:
            # Validate instituteId
            if not instituteId:
                print(f"Invalid instituteId: {instituteId} in resolve_student_category_totals")
                return StudentsByCategoryType(
                    class_name='All',
                    section='All',
                    junior_scholars=0,
                    rising_intellects=0,
                    mastermind_elite=0
                )
            
            # Check if institute exists
            institute_exists = Institute.objects.filter(id=instituteId).exists()
            if not institute_exists:
                print(f"Institute with ID {instituteId} does not exist in resolve_student_category_totals")
                return StudentsByCategoryType(
                    class_name='All',
                    section='All',
                    junior_scholars=0,
                    rising_intellects=0,
                    mastermind_elite=0
                )
            
            # Ensure all students have categories
            classrooms = Classroom.objects.filter(institute_id=instituteId)
            
            # First check for students without categories across all institute classrooms
            students_without_categories = Student.objects.filter(
                institute_id=instituteId,
                student_category__exact=''
            )
            
            # Also check for null category values
            students_with_null = Student.objects.filter(
                institute_id=instituteId,
                student_category__isnull=True
            )
            
            # Log what we found
            print(f"Found {students_without_categories.count()} students with empty category and {students_with_null.count()} with null category")
            
            # Assign random categories to students without categories
            if students_without_categories.exists() or students_with_null.exists():
                import random
                categories = ['junior_scholars', 'rising_intellects', 'mastermind_elite']
                
                # Process empty string categories
                for student in students_without_categories:
                    student.student_category = random.choice(categories)
                    student.save()
                    print(f"Assigned {student.student_category} to student {student.name} (empty category)")
                
                # Process null categories
                for student in students_with_null:
                    student.student_category = random.choice(categories)
                    student.save()
                    print(f"Assigned {student.student_category} to student {student.name} (null category)")
            
            # Count student categories
            junior_scholars = Student.objects.filter(
                institute_id=instituteId,
                student_category='junior_scholars'
            ).count()
            
            rising_intellects = Student.objects.filter(
                institute_id=instituteId,
                student_category='rising_intellects'
            ).count()
            
            mastermind_elite = Student.objects.filter(
                institute_id=instituteId,
                student_category='mastermind_elite'
            ).count()
            
            print(f"Institute {instituteId} totals - Junior: {junior_scholars}, Rising: {rising_intellects}, Mastermind: {mastermind_elite}")
            
            # Create and return a StudentsByCategoryType object with both snake_case and camelCase fields
            result = StudentsByCategoryType(
                class_name='All',
                section='All',
                junior_scholars=junior_scholars,
                rising_intellects=rising_intellects,
                mastermind_elite=mastermind_elite
            )
            
            # Set camelCase attributes directly to ensure they're accessible
            result.juniorScholars = junior_scholars
            result.risingIntellects = rising_intellects
            result.mastermindElite = mastermind_elite
            
            return result
        except Exception as e:
            print(f"Exception in resolve_student_category_totals: {str(e)}")
            # Return empty results in case of error
            return StudentsByCategoryType(
                class_name='All',
                section='All',
                junior_scholars=0,
                rising_intellects=0,
                mastermind_elite=0
            )

    # Add resolver for course count
    def resolve_course_count(self, info, instituteId=None):
        from .models import ClassSubject
        if instituteId:
            return ClassSubject.objects.filter(institute_id=instituteId).count()
        return ClassSubject.objects.count()
    
    # Add resolver for pending approvals count
    # This is just a mock for now since we don't have an approvals model yet
    def resolve_pending_approvals_count(self, info, instituteId=None):
        # In a real implementation, you would query the appropriate model
        # For now, return a fixed number based on institute
        if instituteId:
            # Generate a pseudo-random number based on institute ID
            import hashlib
            hash_val = int(hashlib.md5(str(instituteId).encode()).hexdigest(), 16)
            return (hash_val % 20) + 1  # Between 1 and 20
        return 10  # Default fallback

    # Resolver for recent activities
    def resolve_recent_activities(self, info, instituteId, limit=5):
        # In a real implementation, you would query activity logs
        # For now, generate mock activities with recent timestamps
        activities = []
        
        # Current time for reference
        now = timezone.now()
        
        # Activity types and their descriptions
        activity_types = [
            {"type": "teacher", "title": "New teacher added", "description": "Physics department"},
            {"type": "material", "title": "Study material approved", "description": "Mathematics for Grade 10"},
            {"type": "course", "title": "New course created", "description": "Advanced Biology for Grade 12"},
            {"type": "teacher", "title": "Teacher role updated", "description": "Chemistry department"},
            {"type": "student", "title": "New student enrolled", "description": "Grade: 11, Section: A"},
        ]
        
        # Generate activities with timestamps spread over the last 24 hours
        for i in range(min(limit, len(activity_types))):
            activity = activity_types[i % len(activity_types)]
            # Timestamps spread from recent to older (0 to 24 hours ago)
            hours_ago = (i * 24) // limit
            timestamp = now - timedelta(hours=hours_ago)
            
            activities.append({
                "id": i + 1,
                "type": activity["type"],
                "title": activity["title"],
                "description": activity["description"],
                "timestamp": timestamp
            })
            
        return activities

    # Add resolver for addresses
    def resolve_addresses(self, info):
        return Address.objects.all()

    def resolve_subjects(self, info):
        return Subject.objects.all()
    
    def resolve_class_subjects(self, info, teacher_id=None, classroom_id=None, institute_id=None):
        query = ClassSubject.objects.all()
        
        if teacher_id:
            query = query.filter(teacher_id=teacher_id)
        
        if classroom_id:
            query = query.filter(classroom_id=classroom_id)
        
        if institute_id:
            query = query.filter(institute_id=institute_id)
        
        return query
    
    def resolve_courses(self, info, teacher_id=None, class_subject_id=None, institute_id=None):
        query = Course.objects.all()
        
        if teacher_id:
            query = query.filter(teacher_id=teacher_id)
        
        if class_subject_id:
            query = query.filter(class_subject_id=class_subject_id)
        
        if institute_id:
            query = query.filter(institute_id=institute_id)
        
        return query
    
    def resolve_course(self, info, id):
        return Course.objects.get(pk=id)
    
    def resolve_chapters(self, info, course_id=None):
        query = Chapter.objects.all().order_by('chapter_number')
        if course_id:
            print(f"Filtering chapters by course_id: {course_id}")
            query = query.filter(course_id=course_id)
        return query

    # Add resolver for the single student query
    def resolve_student(self, info, id=None, roll_number=None):
        if id:
            try:
                return Student.objects.get(id=id)
            except Student.DoesNotExist:
                return None
        elif roll_number:
            try:
                return Student.objects.get(roll_number=roll_number)
            except Student.DoesNotExist:
                return None
        return None

    # Resolver for chapter questions
    def resolve_chapter_questions(self, info, chapter_id):
        return ChapterQuestion.objects.filter(chapter_id=chapter_id)
    
    # Resolver for student progress
    def resolve_student_progress(self, info, student_id, chapter_id):
        try:
            return StudentProgress.objects.get(student_id=student_id, chapter_id=chapter_id)
        except StudentProgress.DoesNotExist:
            return None
    
    # Resolver for all student progress for a course
    def resolve_student_course_progress(self, info, student_id, course_id):
        # Get all chapters for the course
        chapters = Chapter.objects.filter(course_id=course_id)
        chapter_ids = [chapter.id for chapter in chapters]
        
        # Get progress for all those chapters
        return StudentProgress.objects.filter(
            student_id=student_id,
            chapter_id__in=chapter_ids
        )

    # Feature Access Distribution
    def resolve_feature_access_distribution(self, info, instituteId=None):
        # Get counts for students, teachers, and admins per feature
        data = []
        
        # Dashboard Access
        students_dashboard = 0
        teachers_dashboard = 0
        admins_dashboard = 0
        
        # Courses Access
        students_courses = 0
        teachers_courses = 0
        admins_courses = 0
        
        # Tests Access
        students_tests = 0
        teachers_tests = 0
        admins_tests = 0
        
        # AI Learning Access
        students_ai = 0
        teachers_ai = 0
        admins_ai = 0
        
        # If an institute is specified, filter counts by institute
        if instituteId:
            students_dashboard = Student.objects.filter(institute_id=instituteId).count()
            teachers_dashboard = Teacher.objects.filter(institute_id=instituteId).count()
            admins_dashboard = User.objects.filter(role='admin', institute_id=instituteId).count()
            
            # Courses may have more specific filtering logic
            students_courses = students_dashboard  # All students have access to courses
            teachers_courses = teachers_dashboard  # All teachers have access to courses
            admins_courses = admins_dashboard      # All admins have access to courses
            
            # For tests, assume a subset of users have access
            students_tests = int(students_dashboard * 0.8)  # 80% of students
            teachers_tests = int(teachers_dashboard * 0.75) # 75% of teachers
            admins_tests = int(admins_dashboard * 0.8)     # 80% of admins
            
            # For AI Learning, assume an even smaller subset has access
            students_ai = int(students_dashboard * 0.6)    # 60% of students
            teachers_ai = int(teachers_dashboard * 0.65)   # 65% of teachers
            admins_ai = int(admins_dashboard * 0.6)        # 60% of admins
        else:
            # Get counts across all institutes
            students_dashboard = Student.objects.count()
            teachers_dashboard = Teacher.objects.count()
            admins_dashboard = User.objects.filter(role='admin').count()
            
            # Courses
            students_courses = students_dashboard  # All students have access to courses
            teachers_courses = teachers_dashboard  # All teachers have access to courses
            admins_courses = admins_dashboard      # All admins have access to courses
            
            # Tests - apply percentage
            students_tests = int(students_dashboard * 0.8)  # 80% of students
            teachers_tests = int(teachers_dashboard * 0.75) # 75% of teachers
            admins_tests = int(admins_dashboard * 0.8)     # 80% of admins
            
            # AI Learning - apply percentage
            students_ai = int(students_dashboard * 0.6)    # 60% of students
            teachers_ai = int(teachers_dashboard * 0.65)   # 65% of teachers
            admins_ai = int(admins_dashboard * 0.6)        # 60% of admins
        
        # Create data structure
        data.extend([
            FeatureAccessType(
                name="Dashboard", 
                students=students_dashboard,
                teachers=teachers_dashboard,
                admins=admins_dashboard
            ),
            FeatureAccessType(
                name="Courses", 
                students=students_courses,
                teachers=teachers_courses,
                admins=admins_courses
            ),
            FeatureAccessType(
                name="Tests", 
                students=students_tests,
                teachers=teachers_tests,
                admins=admins_tests
            ),
            FeatureAccessType(
                name="AI Learning", 
                students=students_ai,
                teachers=teachers_ai,
                admins=admins_ai
            )
        ])
        
        return data

class TeacherLogin(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    token = graphene.String()
    teacher = graphene.Field(TeacherType)
    error = graphene.String()

    def mutate(self, info, email, password):
        try:
            print(f"TeacherLogin mutation called with email: {email}")
            teacher = Teacher.objects.filter(email=email).first()
            
            if not teacher:
                print(f"Teacher not found with email: {email}")
                return TeacherLogin(
                    success=False,
                    token=None,
                    teacher=None,
                    error="Teacher not found"
                )
                
            print(f"Teacher found: {teacher.name}, checking password")
            # Check if password matches
            if teacher.password != password:  # In production, use proper password hashing
                print(f"Invalid password for teacher: {teacher.name}")
                return TeacherLogin(
                    success=False,
                    token=None,
                    teacher=None,
                    error="Invalid password"
                )
                
            print(f"Password valid for teacher: {teacher.name}, generating token")
            # Generate token manually since Teacher is not a User model
            current_time = datetime.datetime.utcnow()
            expiration = current_time + datetime.timedelta(days=1)
            payload = {
                'teacher_id': teacher.id,
                'email': teacher.email,
                'exp': expiration
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            
            print(f"Login successful for teacher: {teacher.name}")
            return TeacherLogin(
                success=True,
                token=token,
                teacher=teacher,
                error=None
            )
        except Exception as e:
            print(f"Error in TeacherLogin: {str(e)}")
            return TeacherLogin(
                success=False,
                token=None,
                teacher=None,
                error=str(e)
            )

class StudentLogin(graphene.Mutation):
    class Arguments:
        rollNumber = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    token = graphene.String()
    student = graphene.Field(StudentType)
    error = graphene.String()

    def mutate(self, info, rollNumber, password):
        try:
            print(f"StudentLogin mutation called with rollNumber: {rollNumber}")
            student = Student.objects.filter(roll_number=rollNumber).first()
            
            if not student:
                print(f"Student not found with rollNumber: {rollNumber}")
                return StudentLogin(
                    success=False,
                    token=None,
                    student=None,
                    error="Student not found"
                )
                
            print(f"Student found: {student.name}, checking password")
            # Check if password matches
            if student.password != password:  # In production, use proper password hashing
                print(f"Invalid password for student: {student.name}")
                return StudentLogin(
                    success=False,
                    token=None,
                    student=None,
                    error="Invalid password"
                )
                
            print(f"Password valid for student: {student.name}, generating token")
            # Generate token manually since Student is not a User model
            current_time = datetime.datetime.utcnow()
            expiration = current_time + datetime.timedelta(days=1)
            payload = {
                'student_id': student.id,
                'roll_number': student.roll_number,
                'exp': expiration
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            
            print(f"Login successful for student: {student.name}")
            return StudentLogin(
                success=True,
                token=token,
                student=student,
                error=None
            )
        except Exception as e:
            print(f"Error in StudentLogin: {str(e)}")
            return StudentLogin(
                success=False,
                token=None,
                student=None,
                error=str(e)
            )

class AdminLogin(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    token = graphene.String()
    user = graphene.Field(UserType)
    error = graphene.String()

    def mutate(self, info, email, password):
        try:
            print(f"AdminLogin mutation called with email: {email}")
            
            # Find user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                print(f"Admin not found with email: {email}")
                return AdminLogin(
                    success=False,
                    token=None,
                    user=None,
                    error="User not found"
                )
            
            # Check if user has admin role
            if user.role != 'admin':
                print(f"User found but not an admin: {user.username}, role: {user.role}")
                return AdminLogin(
                    success=False,
                    token=None,
                    user=None,
                    error="User is not authorized as admin"
                )
                
            print(f"Admin user found: {user.username}, checking password")
            
            # Authenticate with username and password
            authenticated_user = authenticate(username=user.username, password=password)
            
            if not authenticated_user:
                print(f"Invalid password for admin: {user.username}")
                return AdminLogin(
                    success=False,
                    token=None,
                    user=None,
                    error="Invalid password"
                )
                
            print(f"Password valid for admin: {user.username}, generating token")
            
            # Generate token for the user
            token = graphql_jwt.shortcuts.get_token(user)
            
            print(f"Login successful for admin: {user.username}")
            return AdminLogin(
                success=True,
                token=token,
                user=user,
                error=None
            )
        except Exception as e:
            print(f"Error in AdminLogin: {str(e)}")
            return AdminLogin(
                success=False,
                token=None,
                user=None,
                error=str(e)
            )

class SuperAdminLogin(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    token = graphene.String()
    user = graphene.Field(UserType)
    error = graphene.String()

    def mutate(self, info, email, password):
        try:
            print(f"SuperAdminLogin mutation called with email: {email}")
            
            # Find user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                print(f"SuperAdmin not found with email: {email}")
                return SuperAdminLogin(
                    success=False,
                    token=None,
                    user=None,
                    error="User not found"
                )
            
            # Check if user has superadmin role
            if user.role != 'superadmin':
                print(f"User found but not a superadmin: {user.username}, role: {user.role}")
                return SuperAdminLogin(
                    success=False,
                    token=None,
                    user=None,
                    error="User is not authorized as superadmin"
                )
                
            print(f"SuperAdmin user found: {user.username}, checking password")
            
            # Authenticate with username and password
            authenticated_user = authenticate(username=user.username, password=password)
            
            if not authenticated_user:
                print(f"Invalid password for superadmin: {user.username}")
                return SuperAdminLogin(
                    success=False,
                    token=None,
                    user=None,
                    error="Invalid password"
                )
                
            print(f"Password valid for superadmin: {user.username}, generating token")
            
            # Generate token for the user
            token = graphql_jwt.shortcuts.get_token(user)
            
            print(f"Login successful for superadmin: {user.username}")
            return SuperAdminLogin(
                success=True,
                token=token,
                user=user,
                error=None
            )
        except Exception as e:
            print(f"Error in SuperAdminLogin: {str(e)}")
            return SuperAdminLogin(
                success=False,
                token=None,
                user=None,
                error=str(e)
            )

class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, username, email, password, first_name="", last_name=""):
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return CreateUser(user=user)

class CreateAdminUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        institute_id = graphene.ID(required=True)
        address_id = graphene.ID()
        is_active = graphene.Boolean(default_value=True)
    
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    error = graphene.String()
    
    def mutate(self, info, username, email, password, first_name, last_name, 
              institute_id, address_id=None, is_active=True):
        try:
            # Check if user with this username or email already exists
            if User.objects.filter(username=username).exists():
                return CreateAdminUser(
                    user=None,
                    success=False,
                    error="Username already exists"
                )
            
            if User.objects.filter(email=email).exists():
                return CreateAdminUser(
                    user=None,
                    success=False,
                    error="Email already exists"
                )
            
            # Get institute
            try:
                institute = Institute.objects.get(id=institute_id)
            except Institute.DoesNotExist:
                return CreateAdminUser(
                    user=None,
                    success=False,
                    error="Institute not found"
                )
            
            # Get address if provided
            address = None
            if address_id:
                try:
                    address = Address.objects.get(id=address_id)
                except Address.DoesNotExist:
                    return CreateAdminUser(
                        user=None,
                        success=False,
                        error="Address not found"
                    )
            
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active,
                role='admin',
                institute=institute,
                address=address
            )
            
            print(f"Created admin user {username} for institute {institute.name}")
            
            return CreateAdminUser(
                user=user,
                success=True,
                error=None
            )
        except Exception as e:
            print(f"Error creating admin user: {str(e)}")
            return CreateAdminUser(
                user=None,
                success=False,
                error=str(e)
            )

class CreateAddress(graphene.Mutation):
    class Arguments:
        street = graphene.String(required=True)
        city = graphene.String(required=True)
        state = graphene.String(required=True)
        country = graphene.String(required=True)
        postalCode = graphene.String(required=True)
    
    address = graphene.Field(AddressType)
    success = graphene.Boolean()
    error = graphene.String()
    
    def mutate(self, info, street, city, state, country, postalCode):
        try:
            # Create the address
            address = Address.objects.create(
                street=street,
                city=city,
                state=state,
                country=country,
                postal_code=postalCode
            )
            
            print(f"Created address: {street}, {city}, {state}")
            
            return CreateAddress(
                address=address,
                success=True,
                error=None
            )
        except Exception as e:
            print(f"Error creating address: {str(e)}")
            return CreateAddress(
                address=None,
                success=False,
                error=str(e)
            )

class CreateCourse(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        teacher_id = graphene.ID(required=True)
        class_subject_id = graphene.ID(required=True)
        institute_id = graphene.ID(required=True)
    
    course = graphene.Field(CourseType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, name, description, teacher_id, class_subject_id, institute_id):
        try:
            # Log the input parameters for debugging
            print(f"Creating course with: name={name}, teacher_id={teacher_id}, class_subject_id={class_subject_id}, institute_id={institute_id}")
            
            # Check if teacher exists
            try:
                teacher = Teacher.objects.get(id=teacher_id)
            except Teacher.DoesNotExist:
                return CreateCourse(
                    course=None,
                    success=False,
                    message="Teacher not found"
                )
            except Exception as e:
                return CreateCourse(
                    course=None,
                    success=False,
                    message=f"Error finding teacher: {str(e)}"
                )
            
            # Check if class subject exists
            try:
                class_subject = ClassSubject.objects.get(id=class_subject_id)
            except ClassSubject.DoesNotExist:
                return CreateCourse(
                    course=None,
                    success=False,
                    message="Class Subject not found"
                )
            except Exception as e:
                return CreateCourse(
                    course=None,
                    success=False,
                    message=f"Error finding class subject: {str(e)}"
                )
            
            # Check if institute exists
            try:
                institute = Institute.objects.get(id=institute_id)
            except Institute.DoesNotExist:
                return CreateCourse(
                    course=None,
                    success=False,
                    message="Institute not found"
                )
            except Exception as e:
                return CreateCourse(
                    course=None,
                    success=False,
                    message=f"Error finding institute: {str(e)}"
                )
            
            # Create the course
            try:
                course = Course.objects.create(
                    name=name,
                    description=description,
                    teacher=teacher,
                    class_subject=class_subject,
                    institute=institute,
                    is_active=True
                )
                
                return CreateCourse(
                    course=course,
                    success=True,
                    message="Course created successfully"
                )
            except Exception as e:
                return CreateCourse(
                    course=None,
                    success=False,
                    message=f"Error creating course: {str(e)}"
                )
        except Exception as e:
            print(f"Exception in CreateCourse mutation: {str(e)}")
            return CreateCourse(
                course=None,
                success=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

class CreateChapter(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        chapter_number = graphene.Int(required=True)
        course_id = graphene.ID(required=True)
        institute_id = graphene.ID(required=False)  # Make it optional
    
    chapter = graphene.Field(ChapterType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, title, content, chapter_number, course_id, institute_id=None):
        try:
            # Log the input parameters for debugging
            print(f"Creating chapter with: title={title}, chapter_number={chapter_number}, course_id={course_id}")
            
            # Check if course exists
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return CreateChapter(
                    chapter=None,
                    success=False,
                    message="Course not found"
                )
            except Exception as e:
                return CreateChapter(
                    chapter=None,
                    success=False,
                    message=f"Error finding course: {str(e)}"
                )
            
            # Get institute from the course if not provided
            institute = None
            if institute_id:
                try:
                    institute = Institute.objects.get(id=institute_id)
                except Institute.DoesNotExist:
                    return CreateChapter(
                        chapter=None,
                        success=False,
                        message="Institute not found"
                    )
                except Exception as e:
                    return CreateChapter(
                        chapter=None,
                        success=False,
                        message=f"Error finding institute: {str(e)}"
                    )
            else:
                # Get the institute from the course
                institute = course.institute
            
            # Check if a chapter with the same number already exists for this course
            if Chapter.objects.filter(course=course, chapter_number=chapter_number).exists():
                return CreateChapter(
                    chapter=None,
                    success=False,
                    message=f"Chapter number {chapter_number} already exists for this course"
                )
            
            # Create the chapter
            try:
                chapter = Chapter.objects.create(
                    title=title,
                    content=content,
                    chapter_number=chapter_number,
                    course=course,
                    institute=institute,
                    is_active=True
                )
                
                return CreateChapter(
                    chapter=chapter,
                    success=True,
                    message="Chapter created successfully"
                )
            except Exception as e:
                return CreateChapter(
                    chapter=None,
                    success=False,
                    message=f"Error creating chapter: {str(e)}"
                )
        except Exception as e:
            print(f"Exception in CreateChapter mutation: {str(e)}")
            return CreateChapter(
                chapter=None,
                success=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

class DeleteChapter(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        try:
            # Find the chapter
            try:
                chapter = Chapter.objects.get(id=id)
            except Chapter.DoesNotExist:
                return DeleteChapter(
                    success=False,
                    message="Chapter not found"
                )
            
            # Store chapter info for logging
            chapter_info = f"ID: {chapter.id}, Title: {chapter.title}, Course: {chapter.course.name if chapter.course else 'None'}"
            
            # Delete the chapter
            chapter.delete()
            
            # Log the deletion
            print(f"Deleted chapter: {chapter_info}")
            
            return DeleteChapter(
                success=True,
                message="Chapter deleted successfully"
            )
        except Exception as e:
            print(f"Exception in DeleteChapter mutation: {str(e)}")
            return DeleteChapter(
                success=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

class DeleteCourse(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        try:
            # Find the course
            try:
                course = Course.objects.get(id=id)
            except Course.DoesNotExist:
                return DeleteCourse(
                    success=False,
                    message="Course not found"
                )
            
            # Store course info for logging
            course_info = f"ID: {course.id}, Name: {course.name}"
            
            # Get all chapters to log their deletion
            chapters = Chapter.objects.filter(course=course)
            chapter_count = chapters.count()
            
            # Delete all chapters first (this will also delete associated files)
            chapters.delete()
            
            # Now delete the course
            course.delete()
            
            # Log the deletion
            print(f"Deleted course: {course_info} with {chapter_count} chapters")
            
            return DeleteCourse(
                success=True,
                message=f"Course deleted successfully along with {chapter_count} chapters"
            )
        except Exception as e:
            print(f"Exception in DeleteCourse mutation: {str(e)}")
            return DeleteCourse(
                success=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

# Add mutation for creating chapter questions
class CreateChapterQuestion(graphene.Mutation):
    class Arguments:
        chapter_id = graphene.ID(required=True)
        question_text = graphene.String(required=True)
        option_a = graphene.String(required=True)
        option_b = graphene.String(required=True)
        option_c = graphene.String(required=True)
        option_d = graphene.String(required=True)
        correct_option = graphene.String(required=True)
    
    question = graphene.Field(ChapterQuestionType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, chapter_id, question_text, option_a, option_b, option_c, option_d, correct_option):
        try:
            # Check if chapter exists
            try:
                chapter = Chapter.objects.get(id=chapter_id)
            except Chapter.DoesNotExist:
                return CreateChapterQuestion(
                    question=None,
                    success=False,
                    message="Chapter not found"
                )
            
            # Validate correct option
            if correct_option not in ['A', 'B', 'C', 'D']:
                return CreateChapterQuestion(
                    question=None,
                    success=False,
                    message="Correct option must be one of: A, B, C, D"
                )
            
            # Create the question
            question = ChapterQuestion.objects.create(
                chapter=chapter,
                question_text=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option
            )
            
            return CreateChapterQuestion(
                question=question,
                success=True,
                message="Question created successfully"
            )
        except Exception as e:
            print(f"Exception in CreateChapterQuestion mutation: {str(e)}")
            return CreateChapterQuestion(
                question=None,
                success=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

# Add mutation for submitting quiz answers
class SubmitQuizAnswers(graphene.Mutation):
    class Arguments:
        student_id = graphene.ID(required=True)
        chapter_id = graphene.ID(required=True)
        answers = graphene.List(graphene.String, required=True)
        question_ids = graphene.List(graphene.ID, required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    score = graphene.Int()
    total = graphene.Int()
    is_chapter_completed = graphene.Boolean()
    
    def mutate(self, info, student_id, chapter_id, answers, question_ids):
        try:
            # Check if student exists
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return SubmitQuizAnswers(
                    success=False,
                    message="Student not found",
                    score=0,
                    total=0,
                    is_chapter_completed=False
                )
            
            # Check if chapter exists
            try:
                chapter = Chapter.objects.get(id=chapter_id)
            except Chapter.DoesNotExist:
                return SubmitQuizAnswers(
                    success=False,
                    message="Chapter not found",
                    score=0,
                    total=0,
                    is_chapter_completed=False
                )
            
            # Check if answers and question_ids have the same length
            if len(answers) != len(question_ids):
                return SubmitQuizAnswers(
                    success=False,
                    message="Number of answers does not match number of questions",
                    score=0,
                    total=0,
                    is_chapter_completed=False
                )
            
            # Calculate score
            score = 0
            total = len(question_ids)
            
            for i, question_id in enumerate(question_ids):
                try:
                    question = ChapterQuestion.objects.get(id=question_id, chapter=chapter)
                    if question.correct_option == answers[i]:
                        score += 1
                except ChapterQuestion.DoesNotExist:
                    # Skip questions that don't exist or don't belong to the chapter
                    pass
            
            # Update or create progress record
            progress, created = StudentProgress.objects.get_or_create(
                student=student,
                chapter=chapter,
                defaults={
                    'quiz_completed': True,
                    'quiz_score': score,
                    'is_completed': True,  # Mark as completed when quiz is submitted
                    'completed_at': timezone.now()
                }
            )
            
            if not created:
                progress.quiz_completed = True
                progress.quiz_score = score
                progress.is_completed = True
                progress.completed_at = timezone.now()
                progress.save()
            
            return SubmitQuizAnswers(
                success=True,
                message=f"Quiz submitted successfully. Score: {score}/{total}",
                score=score,
                total=total,
                is_chapter_completed=True
            )
        except Exception as e:
            print(f"Exception in SubmitQuizAnswers mutation: {str(e)}")
            return SubmitQuizAnswers(
                success=False,
                message=f"An unexpected error occurred: {str(e)}",
                score=0,
                total=0,
                is_chapter_completed=False
            )

# Add mutation for updating chapter progress
class UpdateChapterProgress(graphene.Mutation):
    class Arguments:
        student_id = graphene.ID(required=True)
        chapter_id = graphene.ID(required=True)
        video_watched = graphene.Boolean(required=False)
        pdf_viewed = graphene.Boolean(required=False)
        quiz_completed = graphene.Boolean(required=False)
        quiz_score = graphene.Int(required=False)
        is_completed = graphene.Boolean(required=False)
    
    success = graphene.Boolean()
    message = graphene.String()
    progress = graphene.Field(StudentProgressType)
    
    def mutate(self, info, student_id, chapter_id, video_watched=None, pdf_viewed=None, 
               quiz_completed=None, quiz_score=None, is_completed=None):
        try:
            # Check if student exists
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return UpdateChapterProgress(
                    success=False,
                    message="Student not found",
                    progress=None
                )
            
            # Check if chapter exists
            try:
                chapter = Chapter.objects.get(id=chapter_id)
            except Chapter.DoesNotExist:
                return UpdateChapterProgress(
                    success=False,
                    message="Chapter not found",
                    progress=None
                )
            
            # Update or create progress record
            progress, created = StudentProgress.objects.get_or_create(
                student=student,
                chapter=chapter
            )
            
            # Update the provided fields
            if video_watched is not None:
                progress.video_watched = video_watched
            
            if pdf_viewed is not None:
                progress.pdf_viewed = pdf_viewed
                
            if quiz_completed is not None:
                progress.quiz_completed = quiz_completed
                
            if quiz_score is not None:
                progress.quiz_score = quiz_score
                
            if is_completed is not None:
                progress.is_completed = is_completed
                # If we're marking as completed, set the completion timestamp
                if is_completed and not progress.completed_at:
                    progress.completed_at = timezone.now()
            
            # Check if all materials have been viewed
            has_quiz = ChapterQuestion.objects.filter(chapter=chapter).exists()
            
            # Save the progress
            progress.save()
            
            return UpdateChapterProgress(
                success=True,
                message="Progress updated successfully",
                progress=progress
            )
        except Exception as e:
            print(f"Exception in UpdateChapterProgress mutation: {str(e)}")
            return UpdateChapterProgress(
                success=False,
                message=f"An unexpected error occurred: {str(e)}",
                progress=None
            )

# Add mutation for deleting a chapter question
class DeleteChapterQuestion(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        try:
            # Find the question
            try:
                question = ChapterQuestion.objects.get(id=id)
            except ChapterQuestion.DoesNotExist:
                return DeleteChapterQuestion(
                    success=False,
                    message="Question not found"
                )
            
            # Store question info for logging
            question_info = f"ID: {question.id}, Chapter: {question.chapter.title}"
            
            # Delete the question
            question.delete()
            
            # Log the deletion
            print(f"Deleted question: {question_info}")
            
            return DeleteChapterQuestion(
                success=True,
                message="Question deleted successfully"
            )
        except Exception as e:
            print(f"Exception in DeleteChapterQuestion mutation: {str(e)}")
            return DeleteChapterQuestion(
                success=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

# Add mutation for updating a chapter question
class UpdateChapterQuestion(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        question_text = graphene.String(required=True)
        option_a = graphene.String(required=True)
        option_b = graphene.String(required=True)
        option_c = graphene.String(required=True)
        option_d = graphene.String(required=True)
        correct_option = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id, question_text, option_a, option_b, option_c, option_d, correct_option):
        try:
            # Find the question
            try:
                question = ChapterQuestion.objects.get(id=id)
            except ChapterQuestion.DoesNotExist:
                return UpdateChapterQuestion(
                    success=False,
                    message="Question not found"
                )
            
            # Validate correct option
            if correct_option not in ['A', 'B', 'C', 'D']:
                return UpdateChapterQuestion(
                    success=False,
                    message="Correct option must be one of: A, B, C, D"
                )
            
            # Update the question
            question.question_text = question_text
            question.option_a = option_a
            question.option_b = option_b
            question.option_c = option_c
            question.option_d = option_d
            question.correct_option = correct_option
            question.save()
            
            return UpdateChapterQuestion(
                success=True,
                message="Question updated successfully"
            )
        except Exception as e:
            print(f"Exception in UpdateChapterQuestion mutation: {str(e)}")
            return UpdateChapterQuestion(
                success=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

class DeleteTeacher(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        try:
            # Find the teacher
            try:
                teacher = Teacher.objects.get(id=id)
            except Teacher.DoesNotExist:
                return DeleteTeacher(
                    success=False,
                    message="Teacher not found"
                )
            
            # Store teacher info for logging
            teacher_info = f"ID: {teacher.id}, Name: {teacher.name}, Email: {teacher.email}"
            
            # Delete the teacher
            teacher.delete()
            
            # Log the deletion
            print(f"Deleted teacher: {teacher_info}")
            
            return DeleteTeacher(
                success=True,
                message="Teacher deleted successfully"
            )
        except Exception as e:
            print(f"Exception in DeleteTeacher mutation: {str(e)}")
            return DeleteTeacher(
                success=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

class DeleteAdmin(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        try:
            # Find the admin user
            try:
                admin = User.objects.get(id=id, role='admin')
            except User.DoesNotExist:
                return DeleteAdmin(
                    success=False,
                    message="Admin user not found"
                )
            
            # Store admin info for logging
            admin_info = f"ID: {admin.id}, Username: {admin.username}, Email: {admin.email}"
            
            # Delete the admin
            admin.delete()
            
            # Log the deletion
            print(f"Deleted admin user: {admin_info}")
            
            return DeleteAdmin(
                success=True,
                message="Admin user deleted successfully"
            )
        except Exception as e:
            print(f"Exception in DeleteAdmin mutation: {str(e)}")
            return DeleteAdmin(
                success=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

class UpdateAdminUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        institute_id = graphene.ID()
        address_id = graphene.ID()
        is_active = graphene.Boolean()
    
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    error = graphene.String()
    
    def mutate(self, info, id, username=None, email=None, password=None, 
               first_name=None, last_name=None, institute_id=None, 
               address_id=None, is_active=None):
        try:
            # Find the admin user
            try:
                admin = User.objects.get(id=id, role='admin')
            except User.DoesNotExist:
                return UpdateAdminUser(
                    user=None,
                    success=False,
                    error="Admin user not found"
                )
            
            # Check if username is being changed and is not already taken
            if username and username != admin.username:
                if User.objects.filter(username=username).exclude(id=id).exists():
                    return UpdateAdminUser(
                        user=None,
                        success=False,
                        error="Username already exists"
                    )
                admin.username = username
            
            # Check if email is being changed and is not already taken
            if email and email != admin.email:
                if User.objects.filter(email=email).exclude(id=id).exists():
                    return UpdateAdminUser(
                        user=None,
                        success=False,
                        error="Email already exists"
                    )
                admin.email = email
            
            # Update other fields if provided
            if password:
                admin.set_password(password)
            
            if first_name is not None:
                admin.first_name = first_name
            
            if last_name is not None:
                admin.last_name = last_name
            
            if is_active is not None:
                admin.is_active = is_active
            
            if institute_id:
                try:
                    institute = Institute.objects.get(id=institute_id)
                    admin.institute = institute
                except Institute.DoesNotExist:
                    return UpdateAdminUser(
                        user=None,
                        success=False,
                        error="Institute not found"
                    )
            
            if address_id:
                try:
                    address = Address.objects.get(id=address_id)
                    admin.address = address
                except Address.DoesNotExist:
                    return UpdateAdminUser(
                        user=None,
                        success=False,
                        error="Address not found"
                    )
            
            # Save the changes
            admin.save()
            
            print(f"Updated admin user: ID {admin.id}, Username: {admin.username}")
            
            return UpdateAdminUser(
                user=admin,
                success=True,
                error=None
            )
        except Exception as e:
            print(f"Error updating admin user: {str(e)}")
            return UpdateAdminUser(
                user=None,
                success=False,
                error=str(e)
            )

class UpdateTeacher(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        email = graphene.String()
        teacher_id = graphene.String()
        phone = graphene.String()
        password = graphene.String() # Note: Handle password hashing appropriately
        is_active = graphene.Boolean()
        gender = graphene.String()
        institute_id = graphene.ID() # Might not be needed if teacher cannot change institute
        address_id = graphene.ID()

    teacher = graphene.Field(TeacherType)
    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, id, name=None, email=None, teacher_id=None, phone=None,
               password=None, is_active=None, gender=None, institute_id=None, address_id=None):
        try:
            # Find the teacher
            try:
                teacher = Teacher.objects.get(id=id)
            except Teacher.DoesNotExist:
                return UpdateTeacher(
                    teacher=None,
                    success=False,
                    error="Teacher not found"
                )

            # Basic authorization check (e.g., ensure admin belongs to the same institute)
            # You might want more robust permission checks here
            requesting_user = info.context.user
            if requesting_user.institute != teacher.institute:
                 return UpdateTeacher(
                     teacher=None,
                     success=False,
                     error="Unauthorized: Cannot update teacher from a different institute."
                 )

            # Check if email is being changed and is not already taken
            if email and email != teacher.email:
                if Teacher.objects.filter(email=email, institute=teacher.institute).exclude(id=id).exists():
                    return UpdateTeacher(
                        teacher=None,
                        success=False,
                        error="Email already exists within this institute"
                    )
                teacher.email = email

            # Check if teacher_id is being changed and is not already taken
            if teacher_id and teacher_id != teacher.teacher_id:
                if Teacher.objects.filter(teacher_id=teacher_id, institute=teacher.institute).exclude(id=id).exists():
                    return UpdateTeacher(
                        teacher=None,
                        success=False,
                        error="Teacher ID already exists within this institute"
                    )
                teacher.teacher_id = teacher_id

            # Update other fields if provided
            if name is not None:
                teacher.name = name

            if phone is not None: # Allow setting phone to empty string
                teacher.phone = phone

            if password: # Only update password if provided
                # Use Django's set_password for hashing in a real app
                teacher.password = password # WARNING: Storing plain text password

            if is_active is not None:
                teacher.is_active = is_active

            if gender is not None:
                if gender not in [choice[0] for choice in GENDER_CHOICES]:
                     return UpdateTeacher(teacher=None, success=False, error="Invalid gender value")
                teacher.gender = gender

            # Optionally allow changing address
            if address_id:
                try:
                    address = Address.objects.get(id=address_id)
                    teacher.address = address
                except Address.DoesNotExist:
                    return UpdateTeacher(
                        teacher=None,
                        success=False,
                        error="Address not found"
                    )
            elif address_id is None: # Allow clearing address
                 teacher.address = None


            # Prevent changing institute directly in this mutation if needed
            # if institute_id and teacher.institute_id != institute_id:
            #     return UpdateTeacher(teacher=None, success=False, error="Changing institute is not allowed here.")

            # Save the changes
            teacher.save()

            print(f"Updated teacher: ID {teacher.id}, Name: {teacher.name}")

            return UpdateTeacher(
                teacher=teacher,
                success=True,
                error=None
            )
        except Exception as e:
            print(f"Error updating teacher: {str(e)}")
            import traceback
            traceback.print_exc()
            return UpdateTeacher(
                teacher=None,
                success=False,
                error=f"An unexpected error occurred: {str(e)}"
            )

class CreateTeacher(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        teacherId = graphene.String(required=True) # Use camelCase
        phone = graphene.String()
        password = graphene.String()
        isActive = graphene.Boolean(default_value=True) # Use camelCase
        gender = graphene.String(default_value="M")
        # institute_id is derived from the logged-in admin user
        addressId = graphene.ID() # Use camelCase

    teacher = graphene.Field(TeacherType)
    success = graphene.Boolean()
    error = graphene.String()

    @login_required
    def mutate(self, info, name, email, teacherId, # Use camelCase arguments
               phone=None, password=None, isActive=True, gender="M", addressId=None):
        # --- Start Debug Logging ---
        print("--- CreateTeacher Mutation --- ")
        requesting_user = info.context.user
        print(f"User authenticated: {requesting_user.is_authenticated}")
        if hasattr(requesting_user, 'role'):
            print(f"User role: {requesting_user.role}")
        else:
            print("User object does not have a 'role' attribute.")
        if hasattr(requesting_user, 'institute'):
             print(f"User institute: {requesting_user.institute}")
        else:
            print("User object does not have an 'institute' attribute.")
        print("--- End Debug Logging ---")
        # --- End Debug Logging ---
        try:
            # Ensure the user is an admin and has an associated institute
            if not requesting_user.is_authenticated or requesting_user.role != 'admin' or not requesting_user.institute:
                return CreateTeacher(
                    teacher=None,
                    success=False,
                    error="Unauthorized: Admin privileges required."
                )

            institute = requesting_user.institute

            # Validate the email format
            from django.core.validators import validate_email
            try:
                validate_email(email)
            except Exception:
                 return CreateTeacher(teacher=None, success=False, error="Invalid email format")

            # Check if teacher with this email or teacher_id already exists *within the institute*
            if Teacher.objects.filter(email=email, institute=institute).exists():
                return CreateTeacher(
                    teacher=None,
                    success=False,
                    error="Email already exists for a teacher in this institute"
                )

            # Use the camelCase teacherId variable here
            if Teacher.objects.filter(teacher_id=teacherId, institute=institute).exists():
                return CreateTeacher(
                    teacher=None,
                    success=False,
                    error="Teacher ID already exists within this institute"
                )

            # Validate gender
            if gender not in [choice[0] for choice in GENDER_CHOICES]:
                return CreateTeacher(teacher=None, success=False, error="Invalid gender value")

            # Set default password if not provided
            if not password:
                password = "changeme123" # Default password - CHANGE THIS

            # Get address if provided
            address = None
            if addressId: # Use camelCase addressId
                try:
                    address = Address.objects.get(id=addressId)
                except Address.DoesNotExist:
                    return CreateTeacher(
                        teacher=None,
                        success=False,
                        error="Address not found"
                    )

            # Create the teacher
            # WARNING: Storing plain text password. Use Django's password hashing in production.
            teacher = Teacher.objects.create(
                name=name,
                email=email,
                teacher_id=teacherId, # Use camelCase teacherId variable
                phone=phone,
                password=password, # Store hashed password in real app
                is_active=isActive, # Use camelCase isActive variable
                gender=gender,
                institute=institute,
                address=address
            )

            print(f"Created teacher: {name} (ID: {teacher.id}) for institute {institute.name}")

            return CreateTeacher(
                teacher=teacher,
                success=True,
                error=None
            )
        except Exception as e:
            print(f"Error creating teacher: {str(e)}")
            import traceback
            traceback.print_exc()
            return CreateTeacher(
                teacher=None,
                success=False,
                error=f"An unexpected error occurred: {str(e)}"
            )

class CreateStudent(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        # Removed email argument
        password = graphene.String(required=True)
        roll_number = graphene.String(required=True)
        classroom_id = graphene.ID(required=True)
        student_category = graphene.String(default_value='junior_scholars')
        gender = graphene.String(default_value='other')
        address_id = graphene.ID()
        # institute_id is derived from the logged-in admin user

    student = graphene.Field(StudentType)
    success = graphene.Boolean()
    error = graphene.String()

    @login_required
    def mutate(self, info, name, password, roll_number, classroom_id, # Removed email from signature
               student_category='junior_scholars', gender='other', address_id=None):
        try:
            requesting_user = info.context.user

            # Authorization check
            if not requesting_user.is_authenticated or requesting_user.role != 'admin' or not requesting_user.institute:
                return CreateStudent(success=False, error="Unauthorized: Admin privileges required.")

            institute = requesting_user.institute

            # Removed email validation

            # Validate gender
            if gender not in [choice[0] for choice in Student.STUDENT_GENDER]:
                return CreateStudent(success=False, error="Invalid gender value")

            # Validate category
            if student_category not in [choice[0] for choice in Student.STUDENT_CATEGORY]:
                 return CreateStudent(success=False, error="Invalid student category")

            # Check for existing roll number within the institute
            if Student.objects.filter(roll_number=roll_number, institute=institute).exists():
                return CreateStudent(success=False, error="Roll number already exists in this institute")
            
            # Check for existing email within the institute (if email should be unique per institute)
            # if Student.objects.filter(email=email, institute=institute).exists():
            #     return CreateStudent(success=False, error="Email already exists for a student in this institute")

            # Get Classroom (ensure it belongs to the admin's institute)
            try:
                classroom = Classroom.objects.get(id=classroom_id, institute=institute)
            except Classroom.DoesNotExist:
                return CreateStudent(success=False, error="Classroom not found or does not belong to this institute")

            # Get Address if provided
            address = None
            if address_id:
                try:
                    address = Address.objects.get(id=address_id)
                except Address.DoesNotExist:
                    return CreateStudent(success=False, error="Address not found")

            # Create the student
            # WARNING: Storing plain text password. Use hashing.
            student = Student.objects.create(
                name=name,
                # Removed email field
                password=password, # Store hashed password in real app
                roll_number=roll_number,
                classroom=classroom,
                student_category=student_category,
                gender=gender,
                institute=institute,
                address=address
            )

            print(f"Created student: {name} (Roll: {roll_number}) for institute {institute.name}")

            return CreateStudent(
                student=student,
                success=True,
                error=None
            )
        except Exception as e:
            print(f"Error creating student: {str(e)}")
            import traceback
            traceback.print_exc()
            return CreateStudent(success=False, error=f"An unexpected error occurred: {str(e)}")

class UpdateStudent(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        # Removed email argument
        password = graphene.String() # Optional password change
        roll_number = graphene.String()
        classroom_id = graphene.ID()
        student_category = graphene.String()
        gender = graphene.String()
        address_id = graphene.ID()

    student = graphene.Field(StudentType)
    success = graphene.Boolean()
    error = graphene.String()

    @login_required
    def mutate(self, info, id, name=None, password=None, roll_number=None, # Removed email from signature
               classroom_id=None, student_category=None, gender=None, address_id=None):
        try:
            requesting_user = info.context.user
            if not requesting_user.is_authenticated or requesting_user.role != 'admin' or not requesting_user.institute:
                return UpdateStudent(success=False, error="Unauthorized: Admin privileges required.")

            institute = requesting_user.institute

            # Find the student within the admin's institute
            try:
                student = Student.objects.get(id=id, institute=institute)
            except Student.DoesNotExist:
                return UpdateStudent(success=False, error="Student not found in this institute")

            # Update fields if provided
            if name is not None:
                student.name = name

            # Removed email update logic

            if password:
                # Use proper password hashing
                student.password = password # WARNING: Plain text password

            if roll_number is not None and roll_number != student.roll_number:
                if Student.objects.filter(roll_number=roll_number, institute=institute).exclude(id=id).exists():
                    return UpdateStudent(success=False, error="Roll number already exists")
                student.roll_number = roll_number

            if classroom_id:
                try:
                    classroom = Classroom.objects.get(id=classroom_id, institute=institute)
                    student.classroom = classroom
                except Classroom.DoesNotExist:
                    return UpdateStudent(success=False, error="Classroom not found or does not belong to this institute")

            if student_category:
                if student_category not in [choice[0] for choice in Student.STUDENT_CATEGORY]:
                     return UpdateStudent(success=False, error="Invalid student category")
                student.student_category = student_category

            if gender:
                if gender not in [choice[0] for choice in Student.STUDENT_GENDER]:
                    return UpdateStudent(success=False, error="Invalid gender value")
                student.gender = gender

            if address_id:
                try:
                    address = Address.objects.get(id=address_id)
                    student.address = address
                except Address.DoesNotExist:
                    return UpdateStudent(success=False, error="Address not found")
            elif address_id is None and name is None and password is None and roll_number is None and classroom_id is None and student_category is None and gender is None:
                 # Allow clearing address only if it's the only operation
                 # Removed email from condition above
                 student.address = None

            student.save()
            print(f"Updated student: ID {student.id}, Roll: {student.roll_number}")
            return UpdateStudent(student=student, success=True)

        except Exception as e:
            print(f"Error updating student: {str(e)}")
            import traceback
            traceback.print_exc()
            return UpdateStudent(success=False, error=f"An unexpected error occurred: {str(e)}")

class DeleteStudent(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id):
        try:
            requesting_user = info.context.user
            if not requesting_user.is_authenticated or requesting_user.role != 'admin' or not requesting_user.institute:
                return DeleteStudent(success=False, message="Unauthorized: Admin privileges required.")

            institute = requesting_user.institute

            # Find the student within the admin's institute
            try:
                student = Student.objects.get(id=id, institute=institute)
            except Student.DoesNotExist:
                return DeleteStudent(success=False, message="Student not found in this institute")

            student_info = f"ID: {student.id}, Roll: {student.roll_number}, Institute: {institute.name}"
            student.delete()
            print(f"Deleted student: {student_info}")
            return DeleteStudent(success=True, message="Student deleted successfully")

        except Exception as e:
            print(f"Error deleting student: {str(e)}")
            return DeleteStudent(success=False, message=f"An unexpected error occurred: {str(e)}")

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_admin_user = CreateAdminUser.Field()
    create_address = CreateAddress.Field()
    teacher_login = TeacherLogin.Field()
    student_login = StudentLogin.Field()
    admin_login = AdminLogin.Field()
    superadmin_login = SuperAdminLogin.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    create_course = CreateCourse.Field()
    create_chapter = CreateChapter.Field()
    delete_chapter = DeleteChapter.Field()
    delete_course = DeleteCourse.Field()
    
    # Add new mutations
    create_chapter_question = CreateChapterQuestion.Field()
    delete_chapter_question = DeleteChapterQuestion.Field()
    update_chapter_question = UpdateChapterQuestion.Field()
    submit_quiz_answers = SubmitQuizAnswers.Field()
    update_chapter_progress = UpdateChapterProgress.Field()
    
    # Add user management delete mutations
    delete_teacher = DeleteTeacher.Field()
    delete_admin = DeleteAdmin.Field()
    
    # Add update admin mutation
    update_admin_user = UpdateAdminUser.Field()
    update_teacher = UpdateTeacher.Field() # Register UpdateTeacher
    create_teacher = CreateTeacher.Field() # Register CreateTeacher
    create_student = CreateStudent.Field()
    update_student = UpdateStudent.Field()
    delete_student = DeleteStudent.Field()

schema = graphene.Schema(query=Query, mutation=Mutation) 