from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix the Student table by adding missing columns'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to fix the Student table...'))
        
        # SQL statements to add the missing columns
        sql_statements = [
            "ALTER TABLE core_student ADD COLUMN student_category VARCHAR(50) NOT NULL DEFAULT 'junior_scholars';",
            "ALTER TABLE core_student ADD COLUMN gender VARCHAR(50) NOT NULL DEFAULT 'male';"
        ]
        
        cursor = connection.cursor()
        
        for sql in sql_statements:
            try:
                self.stdout.write(f"Executing: {sql}")
                cursor.execute(sql)
                self.stdout.write(self.style.SUCCESS(f"Successfully executed: {sql}"))
            except Exception as e:
                # If the column already exists, we'll get an error, which is fine
                self.stdout.write(self.style.WARNING(f"Error executing {sql}: {e}"))
        
        self.stdout.write(self.style.SUCCESS('Student table fix completed!')) 