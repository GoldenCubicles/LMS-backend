# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_add_course_constraints'),
    ]

    operations = [
        # We'll populate data from existing models
        migrations.RunSQL(
            """
            -- Get first institute for initial population
            SET @institute_id = (SELECT id FROM core_institute LIMIT 1);
            
            -- Get first subject for initial population
            SET @subject_id = (SELECT id FROM core_subject LIMIT 1);
            
            -- Get first teacher for initial population
            SET @teacher_id = (SELECT id FROM core_teacher LIMIT 1);
            
            -- Update all courses with null values
            UPDATE core_course
            SET 
                institute_id = @institute_id,
                subject_id = @subject_id,
                teacher_id = @teacher_id
            WHERE 
                institute_id IS NULL OR
                subject_id IS NULL;
            """,
            "SELECT 1;"
        ),
    ] 