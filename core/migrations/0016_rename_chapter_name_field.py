# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_populate_course_references'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Check if chapter_name column exists
            SET @column_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND COLUMN_NAME = 'chapter_name'
            );
            
            -- Only alter the table if the chapter_name column exists
            SET @sql = IF(@column_exists > 0, 
                'ALTER TABLE core_chapter CHANGE COLUMN chapter_name title VARCHAR(255) NOT NULL', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
    ] 