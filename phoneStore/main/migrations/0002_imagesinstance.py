# Generated by Django 5.0.7 on 2024-09-06 17:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImagesInstance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="")),
                (
                    "image_instance_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.productinstance",
                    ),
                ),
            ],
        ),
    ]