from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("guests", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="guest",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddIndex(
            model_name="guest",
            index=models.Index(fields=["is_active"], name="guest_is_active_idx"),
        ),
    ]
