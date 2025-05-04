from django.core.management.base import BaseCommand
from core.models import Teacher, Institute, Address

class Command(BaseCommand):
    help = 'Creates a test teacher for development'

    def handle(self, *args, **options):
        # Create a test institute if it doesn't exist
        institute, created = Institute.objects.get_or_create(
            name="Test Institute",
            defaults={
                "code": "TEST001",
                "address": Address.objects.create(
                    street="123 Test St",
                    city="Test City",
                    state="Test State",
                    country="Test Country",
                    postal_code="12345"
                )
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created test institute: {institute.name}'))
        
        # Create a test teacher
        teacher, created = Teacher.objects.get_or_create(
            email="teacher@example.com",
            defaults={
                "name": "Test Teacher",
                "password": "password",  # In production, use proper password hashing
                "teacher_code": "T001",
                "institute": institute
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created test teacher: {teacher.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Test teacher already exists: {teacher.name}')) 