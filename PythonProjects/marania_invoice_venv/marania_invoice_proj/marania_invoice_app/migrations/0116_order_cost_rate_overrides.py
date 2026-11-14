from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('marania_invoice_app', '0115_merge_20261114_2207'),
    ]
    operations = [
        migrations.AddField(
            model_name='order',
            name='cost_rate_overrides',
            field=models.TextField(blank=True, help_text='JSON {processing,colour,packing,transport} per-kg rates for manual P&L overrides', null=True),
        ),
    ]
