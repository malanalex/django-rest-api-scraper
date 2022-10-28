# Generated by Django 4.1 on 2022-10-28 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0005_alter_pagelink_rel_alter_pagelink_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pagelink",
            name="page",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="links",
                to="pages.page",
            ),
        ),
    ]
