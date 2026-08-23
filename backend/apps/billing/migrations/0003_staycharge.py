from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0002_invoice_notes_invoice_stay_alter_invoice_discount_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StayCharge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "charge_type",
                    models.CharField(
                        choices=[
                            ("SERVICE", "Service"),
                            ("FOOD", "Food"),
                            ("LAUNDRY", "Laundry"),
                            ("DAMAGE", "Damage"),
                            ("LATE_CHECKOUT", "Late checkout"),
                            ("OTHER", "Other"),
                        ],
                        default="SERVICE",
                        max_length=20,
                    ),
                ),
                ("description", models.CharField(max_length=255)),
                ("quantity", models.DecimalField(decimal_places=2, default=1, max_digits=10)),
                ("unit_price", models.DecimalField(decimal_places=2, help_text="Price per unit in NGN", max_digits=12)),
                ("amount", models.DecimalField(decimal_places=2, help_text="Total amount (quantity x unit_price) in NGN", max_digits=12)),
                ("service_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("INVOICED", "Invoiced"), ("VOID", "Void")],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_stay_charges",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="stay_charges",
                        to="billing.invoice",
                    ),
                ),
                (
                    "stay",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="charges", to="stays.stay"),
                ),
            ],
            options={
                "ordering": ["-service_date", "-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="staycharge",
            index=models.Index(fields=["stay"], name="stay_charge_stay_idx"),
        ),
        migrations.AddIndex(
            model_name="staycharge",
            index=models.Index(fields=["invoice"], name="stay_charge_invoice_idx"),
        ),
        migrations.AddIndex(
            model_name="staycharge",
            index=models.Index(fields=["status"], name="stay_charge_status_idx"),
        ),
        migrations.AddIndex(
            model_name="staycharge",
            index=models.Index(fields=["service_date"], name="stay_charge_service_date_idx"),
        ),
        migrations.AddConstraint(
            model_name="staycharge",
            constraint=models.CheckConstraint(condition=models.Q(("quantity__gt", 0)), name="stay_charge_quantity_gt_0"),
        ),
        migrations.AddConstraint(
            model_name="staycharge",
            constraint=models.CheckConstraint(condition=models.Q(("unit_price__gte", 0)), name="stay_charge_unit_price_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="staycharge",
            constraint=models.CheckConstraint(condition=models.Q(("amount__gte", 0)), name="stay_charge_amount_gte_0"),
        ),
    ]
