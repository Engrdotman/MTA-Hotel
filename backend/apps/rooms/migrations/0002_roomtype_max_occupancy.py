from django.db import migrations, models


def copy_capacity_to_occupancy_limits(apps, schema_editor):
    RoomType = apps.get_model("rooms", "RoomType")
    for room_type in RoomType.objects.all():
        capacity = max(room_type.capacity, 1)
        room_type.max_adults = capacity
        room_type.max_children = capacity
        room_type.save(update_fields=["max_adults", "max_children"])


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="roomtype",
            name="max_adults",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="roomtype",
            name="max_children",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.RunPython(copy_capacity_to_occupancy_limits, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="roomtype",
            constraint=models.CheckConstraint(condition=models.Q(max_adults__gt=0), name="room_type_max_adults_gt_0"),
        ),
        migrations.AddConstraint(
            model_name="roomtype",
            constraint=models.CheckConstraint(condition=models.Q(max_children__gte=0), name="room_type_max_children_gte_0"),
        ),
    ]
