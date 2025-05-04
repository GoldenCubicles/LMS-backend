from django.db import models
from django.contrib.auth.models import AbstractUser

# Gender choices for User models
GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}"

class Institute(models.Model):
    name = models.CharField(max_length=255)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
    )
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.role}"

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    teacher_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject, through='TeacherSubject')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    password = models.CharField(max_length=128, default="changeme123")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')

    def __str__(self):
        return self.name

class TeacherSubject(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'subject', 'institute')

    def __str__(self):
        return f"{self.teacher.name} - {self.subject.name}"

class Classroom(models.Model):
    class_name = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    academic_year = models.IntegerField()

    def __str__(self):
        return f"{self.class_name} - {self.section}"

class Student(models.Model):
    STUDENT_CATEGORY = (
        ('junior_scholars', 'Junior Scholars'),
        ('rising_intellects', 'Rising Intellects'),
        ('mastermind_elite', 'Mastermind Elite'),
    )
    STUDENT_GENDER = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    roll_number = models.CharField(max_length=50)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    student_category = models.CharField(max_length=50, choices=STUDENT_CATEGORY)
    gender = models.CharField(max_length=50, choices=STUDENT_GENDER)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('roll_number', 'institute')

    def __str__(self):
        return f"{self.name} ({self.roll_number})"

class ClassSubject(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('classroom', 'subject', 'institute')

    def __str__(self):
        return f"{self.classroom} - {self.subject}"

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, null=True, on_delete=models.SET_NULL)
    class_subject = models.ForeignKey(ClassSubject, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('name', 'institute')

    def __str__(self):
        class_subject_info = ""
        if self.class_subject:
            classroom = self.class_subject.classroom
            subject = self.class_subject.subject
            class_subject_info = f" ({classroom.class_name} {classroom.section} - {subject.name})"
        return f"{self.name}{class_subject_info}"

class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    chapter_number = models.PositiveIntegerField()
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='chapter_pdfs/', null=True, blank=True)
    video_file = models.FileField(upload_to='chapter_videos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('course', 'chapter_number')

    def __str__(self):
        return f"{self.course} - {self.title}"

class ChapterQuestion(models.Model):
    """Model for storing multiple choice questions for chapters"""
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Q{self.id} - {self.chapter.title}"

class StudentProgress(models.Model):
    """Model for tracking student progress through chapters"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='student_progress')
    is_completed = models.BooleanField(default=False)
    video_watched = models.BooleanField(default=False)
    pdf_viewed = models.BooleanField(default=False)
    quiz_completed = models.BooleanField(default=False)
    quiz_score = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'chapter')

    def __str__(self):
        return f"{self.student.name} - {self.chapter.title} - {'Completed' if self.is_completed else 'In Progress'}"

class ChapterMaterial(models.Model):
    MATERIAL_TYPES = (
        ('pdf', 'PDF Document'),
        ('video', 'Video'),
        ('image', 'Image'),
        ('other', 'Other')
    )
    
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True, blank=True)
    file_path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=10, choices=MATERIAL_TYPES)
    file_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        if self.chapter:
            return f"{self.chapter.title} - {self.file_name} ({self.file_type})"
        return f"{self.file_name} ({self.file_type})"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'class_subject')

    def __str__(self):
        return f"{self.student.name} - {self.class_subject}"

class Assignment(models.Model):
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.class_subject}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=255)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title}"
