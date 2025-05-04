# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_fix_course_fields'),
    ]

    operations = [
        # First check if columns exist
        migrations.RunSQL(
            """
            SET @exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_course'
                AND COLUMN_NAME = 'institute_id'
            );
            
            SET @sql = IF(@exists = 0, 'ALTER TABLE core_course ADD COLUMN institute_id BIGINT', 'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
        migrations.RunSQL(
            """
            SET @exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_course'
                AND COLUMN_NAME = 'subject_id'
            );
            
            SET @sql = IF(@exists = 0, 'ALTER TABLE core_course ADD COLUMN subject_id BIGINT', 'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
        migrations.RunSQL(
            """
            SET @exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_course'
                AND COLUMN_NAME = 'teacher_id'
            );
            
            SET @sql = IF(@exists = 0, 'ALTER TABLE core_course ADD COLUMN teacher_id BIGINT', 'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
    ] 