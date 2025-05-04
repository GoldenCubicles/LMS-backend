# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_add_chapter_fields'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Add course_id column if it doesn't exist
            SET @course_id_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND COLUMN_NAME = 'course_id'
            );
            
            SET @sql = IF(@course_id_exists = 0, 
                'ALTER TABLE core_chapter ADD COLUMN course_id BIGINT NULL', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            
            -- Add foreign key constraint for course_id
            SET @constraint_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND COLUMN_NAME = 'course_id'
                AND REFERENCED_TABLE_NAME = 'core_course'
            );
            
            SET @sql = IF(@constraint_exists = 0, 
                'ALTER TABLE core_chapter ADD CONSTRAINT fk_chapter_course_id FOREIGN KEY (course_id) REFERENCES core_course(id)', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            
            -- Update the unique constraints
            SET @unique_constraint_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND CONSTRAINT_TYPE = 'UNIQUE'
                AND CONSTRAINT_NAME = 'core_chapter_course_id_chapter_number_unique'
            );
            
            -- If unique constraint doesn't exist, add it
            SET @sql = IF(@unique_constraint_exists = 0, 
                'ALTER TABLE core_chapter ADD CONSTRAINT core_chapter_course_id_chapter_number_unique UNIQUE (course_id, chapter_number)', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
    ] 