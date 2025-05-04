from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AddressViewSet, InstituteViewSet, UserViewSet, SubjectViewSet,
    TeacherViewSet, TeacherSubjectViewSet, ClassroomViewSet,
    StudentViewSet, ClassSubjectViewSet, ChapterViewSet,
    EnrollmentViewSet, AssignmentViewSet, SubmissionViewSet,
    login_view, admin_login, upload_chapter_files
)

router = DefaultRouter()
router.register(r'addresses', AddressViewSet)
router.register(r'institutes', InstituteViewSet)
router.register(r'users', UserViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'teacher-subjects', TeacherSubjectViewSet)
router.register(r'classrooms', ClassroomViewSet)
router.register(r'students', StudentViewSet)
router.register(r'class-subjects', ClassSubjectViewSet)
router.register(r'chapters', ChapterViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'submissions', SubmissionViewSet)

urlpatterns = [
    path('auth/admin/login/', admin_login, name='admin-login'),
    path('login/', login_view, name='login'),
    path('upload-chapter-files/', upload_chapter_files, name='upload-chapter-files'),
    path('', include(router.urls)),
] 