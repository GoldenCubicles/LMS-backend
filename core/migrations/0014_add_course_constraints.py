# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_fix_course_table'),
    ]

    operations = [
        # Add foreign key constraints if they don't exist
        migrations.RunSQL(
            """
            SET @constraint_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_course'
                AND CONSTRAINT_NAME = 'fk_course_institute_id'
            );
            
            SET @sql = IF(@constraint_exists = 0, 
                'ALTER TABLE core_course ADD CONSTRAINT fk_course_institute_id FOREIGN KEY (institute_id) REFERENCES core_institute(id)', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
        migrations.RunSQL(
            """
            SET @constraint_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_course'
                AND CONSTRAINT_NAME = 'fk_course_subject_id'
            );
            
            SET @sql = IF(@constraint_exists = 0, 
                'ALTER TABLE core_course ADD CONSTRAINT fk_course_subject_id FOREIGN KEY (subject_id) REFERENCES core_subject(id)', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
        migrations.RunSQL(
            """
            SET @constraint_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_course'
                AND CONSTRAINT_NAME = 'fk_course_teacher_id'
            );
            
            SET @sql = IF(@constraint_exists = 0, 
                'ALTER TABLE core_course ADD CONSTRAINT fk_course_teacher_id FOREIGN KEY (teacher_id) REFERENCES core_teacher(id)', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
        # Add unique constraint for name and institute_id
        migrations.RunSQL(
            """
            SET @constraint_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_course'
                AND CONSTRAINT_NAME = 'unique_name_institute'
            );
            
            SET @sql = IF(@constraint_exists = 0, 
                'ALTER TABLE core_course ADD CONSTRAINT unique_name_institute UNIQUE (name, institute_id)', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
    ] 