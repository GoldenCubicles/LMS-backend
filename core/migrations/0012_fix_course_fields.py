# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_add_class_subject_to_course'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL to recreate relationships if they're missing
            """
            ALTER TABLE core_course 
            ADD COLUMN institute_id BIGINT NULL,
            ADD COLUMN subject_id BIGINT NULL,
            ADD COLUMN teacher_id BIGINT NULL;
            """,
            # Reverse SQL
            """
            -- No reverse SQL needed, fields should exist
            """
        ),
        migrations.RunSQL(
            # SQL to update foreign key constraints
            """
            ALTER TABLE core_course
            ADD CONSTRAINT fk_course_institute_id FOREIGN KEY (institute_id) REFERENCES core_institute(id),
            ADD CONSTRAINT fk_course_subject_id FOREIGN KEY (subject_id) REFERENCES core_subject(id),
            ADD CONSTRAINT fk_course_teacher_id FOREIGN KEY (teacher_id) REFERENCES core_teacher(id);
            """,
            # Reverse SQL
            """
            ALTER TABLE core_course
            DROP FOREIGN KEY fk_course_institute_id,
            DROP FOREIGN KEY fk_course_subject_id,
            DROP FOREIGN KEY fk_course_teacher_id;
            """
        ),
    ] 