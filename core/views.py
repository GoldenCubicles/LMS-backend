from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import (
    Address, Institute, User, Subject, Teacher, TeacherSubject,
    Classroom, Student, ClassSubject, Chapter, Enrollment,
    Assignment, Submission, ChapterMaterial
)
from .serializers import (
    AddressSerializer, InstituteSerializer, UserSerializer, SubjectSerializer,
    TeacherSerializer, TeacherSubjectSerializer, ClassroomSerializer,
    StudentSerializer, ClassSubjectSerializer, ChapterSerializer,
    EnrollmentSerializer, AssignmentSerializer, SubmissionSerializer
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json

# Create your views here.

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

class InstituteViewSet(viewsets.ModelViewSet):
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(institute=self.request.user.institute)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Teacher.objects.all()
        return Teacher.objects.filter(institute=self.request.user.institute)

class TeacherSubjectViewSet(viewsets.ModelViewSet):
    queryset = TeacherSubject.objects.all()
    serializer_class = TeacherSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return TeacherSubject.objects.all()
        return TeacherSubject.objects.filter(institute=self.request.user.institute)

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Classroom.objects.all()
        return Classroom.objects.filter(institute=self.request.user.institute)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Student.objects.all()
        return Student.objects.filter(institute=self.request.user.institute)

class ClassSubjectViewSet(viewsets.ModelViewSet):
    queryset = ClassSubject.objects.all()
    serializer_class = ClassSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return ClassSubject.objects.all()
        return ClassSubject.objects.filter(institute=self.request.user.institute)

class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Chapter.objects.all()
        return Chapter.objects.filter(institute=self.request.user.institute)

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Enrollment.objects.all()
        return Enrollment.objects.filter(institute=self.request.user.institute)

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Assignment.objects.all()
        return Assignment.objects.filter(class_subject__institute=self.request.user.institute)

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Submission.objects.all()
        return Submission.objects.filter(assignment__class_subject__institute=self.request.user.institute)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if email and not username:
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            return Response(
                {'error': 'No user found with this email'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user)
        
        return Response({
            'user': serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def admin_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'message': 'Email and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
        if user.role not in ['admin', 'manager']:
            return Response(
                {'message': 'User is not authorized'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    except User.DoesNotExist:
        return Response(
            {'message': 'No user found with this email'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    authenticated_user = authenticate(username=user.username, password=password)
    
    if authenticated_user is not None:
        refresh = RefreshToken.for_user(authenticated_user)
        return Response({
            'token': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'institute': user.institute.id if user.institute else None
            }
        })
    else:
        return Response(
            {'message': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@csrf_exempt
def upload_chapter_files(request):
    if request.method == 'POST':
        try:
            print("Upload chapter files request received")
            # Get chapter ID from the request
            chapter_id = request.POST.get('chapter_id')
            
            if not chapter_id:
                print("Missing chapter ID")
                return JsonResponse({
                    'success': False,
                    'message': 'Chapter ID is required'
                }, status=400)
            
            print(f"Processing files for chapter ID: {chapter_id}")
            
            # Check if chapter exists
            try:
                chapter = Chapter.objects.get(id=chapter_id)
                print(f"Found chapter: {chapter.title}")
            except Chapter.DoesNotExist:
                print(f"Chapter not found with ID: {chapter_id}")
                return JsonResponse({
                    'success': False,
                    'message': 'Chapter not found'
                }, status=404)
            
            # Handle PDF file upload
            if 'pdf_file' in request.FILES:
                pdf_file = request.FILES['pdf_file']
                print(f"Processing PDF file: {pdf_file.name}")
                
                # Directly update the chapter model
                chapter.pdf_file = pdf_file
                chapter.save(update_fields=['pdf_file'])
                print(f"PDF file saved to chapter: {chapter.pdf_file.url if chapter.pdf_file else 'None'}")
            
            # Handle Video file upload
            if 'video_file' in request.FILES:
                video_file = request.FILES['video_file']
                print(f"Processing Video file: {video_file.name}")
                
                # Directly update the chapter model
                chapter.video_file = video_file
                chapter.save(update_fields=['video_file'])
                print(f"Video file saved to chapter: {chapter.video_file.url if chapter.video_file else 'None'}")
            
            return JsonResponse({
                'success': True,
                'message': 'Files uploaded successfully',
                'data': {
                    'chapter_id': chapter.id,
                    'pdf_file': chapter.pdf_file.url if chapter.pdf_file else None,
                    'video_file': chapter.video_file.url if chapter.video_file else None
                }
            })
            
        except Exception as e:
            print(f"Error in upload_chapter_files: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error uploading files: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Only POST requests are allowed'
    }, status=405)
