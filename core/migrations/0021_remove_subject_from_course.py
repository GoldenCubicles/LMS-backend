# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_update_chapter_with_course'),
    ]

    operations = [
        # First, check and drop the foreign key constraint
        migrations.RunSQL(
            """
            -- Check if foreign key constraint exists
            SET @fk_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_course'
                AND COLUMN_NAME = 'subject_id'
                AND REFERENCED_TABLE_NAME = 'core_subject'
            );
            
            -- If foreign key exists, drop the constraint
            SET @constraint_name = (
                SELECT CONSTRAINT_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_course'
                AND COLUMN_NAME = 'subject_id'
                AND REFERENCED_TABLE_NAME = 'core_subject'
                LIMIT 1
            );
            
            SET @sql = IF(@fk_exists > 0, 
                CONCAT('ALTER TABLE core_course DROP FOREIGN KEY ', @constraint_name), 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            
            -- Now drop the column
            SET @column_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_course'
                AND COLUMN_NAME = 'subject_id'
            );
            
            SET @sql = IF(@column_exists > 0, 
                'ALTER TABLE core_course DROP COLUMN subject_id', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            # Rollback SQL - would need to recreate the column and ForeignKey
            """
            ALTER TABLE core_course ADD COLUMN subject_id BIGINT NULL;
            ALTER TABLE core_course ADD CONSTRAINT fk_course_subject_id FOREIGN KEY (subject_id) REFERENCES core_subject(id);
            """
        ),
    ] 