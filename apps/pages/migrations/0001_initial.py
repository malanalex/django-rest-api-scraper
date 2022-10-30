# Generated by Django 4.1 on 2022-10-30 14:43

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
                ("processed_at", models.DateTimeField(null=True)),
                ("url", models.URLField(max_length=600, unique=True)),
                ("stats", models.JSONField(null=True)),
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
                ("href", models.CharField(max_length=600)),
                ("rel", models.CharField(max_length=600, null=True)),
                ("title", models.CharField(max_length=600, null=True)),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="links",
                        to="pages.page",
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
