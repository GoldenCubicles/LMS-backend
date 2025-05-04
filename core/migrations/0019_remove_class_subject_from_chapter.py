# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_remove_class_subject_add_course_to_chapter'),
    ]

    operations = [
        # First, let's update course_id based on class_subject where possible
        migrations.RunSQL(
            """
            -- Update course_id based on class_subject
            UPDATE core_chapter ch
            JOIN core_classsubject cs ON ch.class_subject_id = cs.id
            JOIN core_course c ON c.class_subject_id = cs.id
            SET ch.course_id = c.id
            WHERE ch.class_subject_id IS NOT NULL
              AND ch.course_id IS NULL;
            
            -- If some chapters still have NULL course_id, use first course available
            SET @default_course = (SELECT id FROM core_course LIMIT 1);
            
            UPDATE core_chapter 
            SET course_id = @default_course
            WHERE course_id IS NULL;
            """,
            "SELECT 1;"
        ),
        # Now remove the unique constraint on class_subject_id and chapter_number
        migrations.RunSQL(
            """
            -- Check if the constraint exists
            SET @unique_key_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND CONSTRAINT_TYPE = 'UNIQUE'
                AND CONSTRAINT_NAME = 'core_chapter_class_subject_id_chapter_number_uniq'
            );
            
            -- If constraint exists, drop it
            SET @sql = IF(@unique_key_exists > 0, 
                'ALTER TABLE core_chapter DROP INDEX core_chapter_class_subject_id_chapter_number_uniq', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
        # Finally, drop the foreign key and column
        migrations.RunSQL(
            """
            -- Check if foreign key constraint exists
            SET @fk_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND COLUMN_NAME = 'class_subject_id'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            );
            
            -- If foreign key exists, first drop the constraint
            SET @constraint_name = (
                SELECT CONSTRAINT_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND COLUMN_NAME = 'class_subject_id'
                AND REFERENCED_TABLE_NAME IS NOT NULL
                LIMIT 1
            );
            
            SET @sql = IF(@fk_exists > 0, 
                CONCAT('ALTER TABLE core_chapter DROP FOREIGN KEY ', @constraint_name), 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            
            -- Now drop the column
            SET @column_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND COLUMN_NAME = 'class_subject_id'
            );
            
            SET @sql = IF(@column_exists > 0, 
                'ALTER TABLE core_chapter DROP COLUMN class_subject_id', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
    ] 