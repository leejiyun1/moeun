from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0005_feedback_image_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedback",
            name="positive_tags",
            field=models.JSONField(blank=True, default=list, help_text="좋았던 점 태그 목록"),
        ),
        migrations.AddField(
            model_name="feedback",
            name="negative_tags",
            field=models.JSONField(blank=True, default=list, help_text="아쉬웠던 점 태그 목록"),
        ),
    ]
