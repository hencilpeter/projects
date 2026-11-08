# Generated for manual twine price overrides on Sales

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marania_invoice_app', '0106_sales_profit_loss'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='twine_price_overrides',
            field=models.TextField(blank=True, help_text='JSON {material_code: price_per_kg_incl_gst} for manual P&L overrides', null=True),
        ),
    ]
