# Generated by Django 4.1.2 on 2023-02-15 20:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0012_alter_assessment_weighting_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='class_head_level',
        ),
        migrations.CreateModel(
            name='LevelHead',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('level', models.IntegerField(choices=[(1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3'), (4, 'Level 4'), (5, 'Level 5'), (10, 'All levels')], default=0)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level_heads', to='general.academicyear')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level_head', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
