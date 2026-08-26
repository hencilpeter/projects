# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marania_invoice_app', '0089_add_default_bag_weight_to_company_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='profitanalytics',
            name='specification',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
