from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('marania_invoice_app', '0111_pricelistconfiguration_price_overrides'),
    ]
    operations = [
        migrations.AddField(
            model_name='pricelistconfiguration',
            name='mesh_label_overrides',
            field=models.TextField(blank=True, default='{}'),
        ),
    ]
