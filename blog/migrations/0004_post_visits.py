# Generated by Django 2.1.2 on 2018-12-02 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20181202_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='visits',
            field=models.IntegerField(default=0),
        ),
    ]