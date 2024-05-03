# Generated by Django 5.0.3 on 2024-05-03 09:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0003_remove_recipe_cluster_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ingredient",
            name="tfidf_value",
            field=models.FloatField(
                default=0.0,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(1.0),
                ],
            ),
        ),
    ]
