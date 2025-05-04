# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_remove_class_subject_from_chapter'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE core_chapter
            ADD CONSTRAINT core_chapter_course_id_chapter_number_uniq 
            UNIQUE (course_id, chapter_number);
            """,
            reverse_sql="""
            ALTER TABLE core_chapter
            DROP INDEX core_chapter_course_id_chapter_number_uniq;
            """
        ),
    ] 