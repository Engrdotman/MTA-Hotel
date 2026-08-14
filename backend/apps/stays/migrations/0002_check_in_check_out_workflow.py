# Generated for the Check-in / Check-out MVP.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def map_statuses_forward(apps, schema_editor):
    Stay = apps.get_model("stays", "Stay")
    Stay.objects.filter(status="ACTIVE").update(status="CHECKED_IN")
    Stay.objects.filter(status__in=["COMPLETED", "CANCELLED"]).update(status="CHECKED_OUT")


def map_statuses_backward(apps, schema_editor):
    Stay = apps.get_model("stays", "Stay")
    Stay.objects.filter(status="CHECKED_IN").update(status="ACTIVE")
    Stay.objects.filter(status="CHECKED_OUT").update(status="COMPLETED")


class Migration(migrations.Migration):

    dependencies = [
        ("stays", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name="stay",
            old_name="actual_check_in",
            new_name="checked_in_at",
        ),
        migrations.RenameField(
            model_name="stay",
            old_name="actual_check_out",
            new_name="checked_out_at",
        ),
        migrations.RenameField(
            model_name="stay",
            old_name="created_by",
            new_name="checked_in_by",
        ),
        migrations.AddField(
            model_name="stay",
            name="checked_out_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="checked_out_stays",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="stay",
            name="notes",
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(map_statuses_forward, map_statuses_backward),
        migrations.AlterField(
            model_name="stay",
            name="checked_in_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="checked_in_stays",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="stay",
            name="status",
            field=models.CharField(
                choices=[("CHECKED_IN", "Checked in"), ("CHECKED_OUT", "Checked out")],
                default="CHECKED_IN",
                max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name="stay",
            options={"ordering": ["-checked_in_at"]},
        ),
        migrations.AddIndex(
            model_name="stay",
            index=models.Index(fields=["checked_in_at"], name="stay_checked_in_idx"),
        ),
        migrations.AddIndex(
            model_name="stay",
            index=models.Index(fields=["checked_out_at"], name="stay_checked_out_idx"),
        ),
        migrations.AddConstraint(
            model_name="stay",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "CHECKED_IN")),
                fields=("reservation",),
                name="unique_active_stay_per_reservation",
            ),
        ),
    ]
