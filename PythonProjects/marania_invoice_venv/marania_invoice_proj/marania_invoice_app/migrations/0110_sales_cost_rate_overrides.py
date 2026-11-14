# Generated for manual per-kg cost rate overrides on Sales

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marania_invoice_app', '0109_profitloss_material_sales_profit'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='cost_rate_overrides',
            field=models.TextField(blank=True, help_text='JSON {processing,colour,packing,transport} per-kg rates for manual P&L overrides', null=True),
        ),
    ]
