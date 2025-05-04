from django.core.management.base import BaseCommand
from django.db import connection
import os
import re

class Command(BaseCommand):
    help = 'Seeds the database with dummy data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to seed the database...'))
        
        # Path to the SQL file
        sql_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'seed_data.sql')
        
        if not os.path.exists(sql_file_path):
            self.stdout.write(self.style.ERROR(f'SQL file not found: {sql_file_path}'))
            return
        
        # Read the SQL file
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
        
        # Better splitting for MySQL - respects comment blocks and handles multi-line statements
        statements = []
        current_statement = ""
        for line in sql_script.splitlines():
            # Skip comments
            if line.strip().startswith('--'):
                continue
                
            # Add to current statement
            current_statement += line + " "
            
            # If line ends with semicolon, this statement is complete
            if line.strip().endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        # Execute each statement
        cursor = connection.cursor()
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            try:
                if not statement.strip():
                    continue
                
                # Extract the type of statement for better logging
                statement_type = "SQL"
                match = re.match(r'^\s*(INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|SELECT)\s+', statement, re.IGNORECASE)
                if match:
                    statement_type = match.group(1).upper()
                
                self.stdout.write(f"Executing {statement_type} statement {i}...")
                cursor.execute(statement)
                connection.commit()
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"{statement_type} statement {i} executed successfully"))
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"Error executing statement {i}: {e}"))
                # Continue with other statements even if one fails
        
        self.stdout.write(self.style.SUCCESS(f'Database seeding completed! {success_count} statements executed successfully, {error_count} errors')) 