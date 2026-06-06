from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0011_simplify_product_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="brewery",
            name="homepage_url",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name="drink",
            name="food_pairing",
            field=models.TextField(blank=True),
        ),
    ]
