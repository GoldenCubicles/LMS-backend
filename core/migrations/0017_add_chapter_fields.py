# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_rename_chapter_name_field'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Add created_at and updated_at columns if they don't exist
            SET @created_at_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND COLUMN_NAME = 'created_at'
            );
            
            SET @sql = IF(@created_at_exists = 0, 
                'ALTER TABLE core_chapter ADD COLUMN created_at DATETIME(6) NOT NULL DEFAULT NOW(6)', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            
            SET @updated_at_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND COLUMN_NAME = 'updated_at'
            );
            
            SET @sql = IF(@updated_at_exists = 0, 
                'ALTER TABLE core_chapter ADD COLUMN updated_at DATETIME(6) NOT NULL DEFAULT NOW(6)', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            
            SET @is_active_exists = (
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_chapter'
                AND COLUMN_NAME = 'is_active'
            );
            
            SET @sql = IF(@is_active_exists = 0, 
                'ALTER TABLE core_chapter ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1', 
                'SELECT 1');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            "SELECT 1;"
        ),
    ] 