# Generated by Django 4.1.4 on 2023-09-20 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_user_user_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_icon',
            field=models.ImageField(blank=True, null=True, upload_to='socialSimon/accounts/user_icons/'),
        ),
    ]
