# Generated by Django 4.1 on 2022-10-23 11:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Page",
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
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField()),
                ("url", models.CharField(max_length=255)),
                ("stats", models.JSONField()),
            ],
            options={
                "verbose_name": "Page",
                "verbose_name_plural": "Pages",
                "db_table": "pages",
            },
        ),
        migrations.CreateModel(
            name="PageLink",
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
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("href", models.CharField(max_length=255)),
                ("rel", models.CharField(max_length=255)),
                ("title", models.CharField(max_length=255)),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="pages.page"
                    ),
                ),
            ],
            options={
                "verbose_name": "PageLink",
                "verbose_name_plural": "PageLinks",
                "db_table": "pagelinks",
            },
        ),
    ]