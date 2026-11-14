from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('marania_invoice_app', '0110_sales_cost_rate_overrides'),
    ]
    operations = [
        migrations.AddField(
            model_name='pricelistconfiguration',
            name='price_overrides',
            field=models.TextField(blank=True, default='{}'),
        ),
    ]
