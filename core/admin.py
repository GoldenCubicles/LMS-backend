from django.contrib import admin
from .models import (
    Address, Institute, User, Subject, Teacher, TeacherSubject,
    Classroom, Student, ClassSubject, Chapter, Enrollment,
    Assignment, Submission, Course, ChapterMaterial, ChapterQuestion, StudentProgress
)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'city', 'state', 'country', 'postal_code')
    search_fields = ('street', 'city', 'state', 'country', 'postal_code')

@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'institute')
    list_filter = ('role', 'institute')
    search_fields = ('username', 'email')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'teacher_id', 'institute')
    list_filter = ('institute',)
    search_fields = ('name', 'email', 'teacher_id')

@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'institute')
    list_filter = ('institute', 'subject')
    search_fields = ('teacher__name', 'subject__name')

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'section', 'class_teacher', 'institute', 'academic_year')
    list_filter = ('institute', 'academic_year')
    search_fields = ('class_name', 'section')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'classroom', 'institute')
    list_filter = ('institute', 'classroom')
    search_fields = ('name', 'roll_number')

@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'subject', 'teacher', 'institute')
    list_filter = ('institute', 'subject')
    search_fields = ('classroom__class_name', 'subject__name', 'teacher__name')

# Register ChapterQuestion as an inline for Chapter
class ChapterQuestionInline(admin.TabularInline):
    model = ChapterQuestion
    extra = 1
    fields = ('question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option')

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'chapter_number', 'has_pdf', 'has_video', 'has_questions', 'is_active')
    list_filter = ('course', 'is_active')
    search_fields = ('title', 'content')
    inlines = [ChapterQuestionInline]
    
    def has_pdf(self, obj):
        # Check if there's a direct PDF file attached
        return bool(obj.pdf_file)
    has_pdf.boolean = True
    has_pdf.short_description = 'PDF'
    
    def has_video(self, obj):
        # Check if there's a direct video file attached
        return bool(obj.video_file)
    has_video.boolean = True
    has_video.short_description = 'Video'
    
    def has_questions(self, obj):
        # Check if there are any questions for this chapter
        return obj.questions.exists()
    has_questions.boolean = True
    has_questions.short_description = 'MCQs'

# Register ChapterQuestion model in admin
@admin.register(ChapterQuestion)
class ChapterQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter', 'question_text', 'correct_option')
    list_filter = ('chapter', 'correct_option')
    search_fields = ('question_text', 'chapter__title')

# Register StudentProgress model in admin
@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'chapter', 'is_completed', 'quiz_score', 'completed_at')
    list_filter = ('is_completed', 'quiz_completed', 'video_watched', 'pdf_viewed')
    search_fields = ('student__name', 'chapter__title')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_subject', 'institute', 'enrollment_date')
    list_filter = ('institute', 'enrollment_date')
    search_fields = ('student__name', 'class_subject__subject__name')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_subject', 'due_date', 'created_at')
    list_filter = ('due_date', 'created_at')
    search_fields = ('title',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submission_date')
    list_filter = ('submission_date',)
    search_fields = ('student__name', 'assignment__title')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_class_info', 'get_subject_info', 'teacher', 'institute', 'is_active')
    list_filter = ('institute', 'is_active', 'class_subject__classroom__class_name')
    search_fields = ('name', 'description', 'teacher__name', 'class_subject__classroom__class_name')
    date_hierarchy = 'created_at'
    
    def get_class_info(self, obj):
        if obj.class_subject and obj.class_subject.classroom:
            return f"{obj.class_subject.classroom.class_name} {obj.class_subject.classroom.section}"
        return "-"
    get_class_info.short_description = "Class"
    
    def get_subject_info(self, obj):
        if obj.class_subject and obj.class_subject.subject:
            return obj.class_subject.subject.name
        return "-"
    get_subject_info.short_description = "Subject"
