# Generated by Django 4.2.1 on 2023-10-02 07:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_remove_user_user_icon_alter_user_user_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('class_id', models.AutoField(primary_key=True, serialize=False)),
                ('class_code', models.CharField(max_length=255)),
                ('class_description', models.TextField(blank=True, null=True)),
                ('class_domain', models.CharField(blank=True, max_length=255, null=True)),
                ('class_campus', models.CharField(blank=True, max_length=255, null=True)),
                ('class_teacher_code', models.CharField(blank=True, max_length=255, null=True)),
                ('class_teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes_taught', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='userclassesrelationship',
            name='class_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.class'),
        ),
    ]