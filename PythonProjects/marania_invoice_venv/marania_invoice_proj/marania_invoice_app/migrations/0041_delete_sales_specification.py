from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marania_invoice_app', '0040_migrate_sales_spec_data'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SalesSpecification',
        ),
    ]
