# Generated by Django 4.2.5 on 2023-11-18 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_app', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RollNumber',
        ),
        migrations.AddField(
            model_name='school_file',
            name='course',
            field=models.CharField(default='default_course_value', max_length=100),
        ),
    ]
