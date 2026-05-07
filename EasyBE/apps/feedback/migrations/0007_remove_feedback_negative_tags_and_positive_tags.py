from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0006_feedback_positive_tags_feedback_negative_tags"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="feedback",
            name="negative_tags",
        ),
        migrations.RemoveField(
            model_name="feedback",
            name="positive_tags",
        ),
    ]
