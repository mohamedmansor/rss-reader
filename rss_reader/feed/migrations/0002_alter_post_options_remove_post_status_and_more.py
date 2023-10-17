# Generated by Django 4.2.6 on 2023-10-14 00:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("feed", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="post",
            options={"ordering": ["-last_update"], "verbose_name": "Post", "verbose_name_plural": "Posts"},
        ),
        migrations.RemoveField(
            model_name="post",
            name="status",
        ),
        migrations.RemoveField(
            model_name="userfeed",
            name="followed",
        ),
    ]