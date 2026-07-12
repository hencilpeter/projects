# Generated automatically

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marania_invoice_app', '0021_alter_materials_supplier'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_number', models.CharField(max_length=100)),
                ('order_date', models.DateField()),
                ('twine', models.CharField(blank=True, max_length=255, null=True)),
                ('mesh_size', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('mesh_depth', models.CharField(blank=True, max_length=50, null=True)),
                ('salvage', models.CharField(blank=True, max_length=255, null=True)),
                ('piece_weight', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity_unit', models.CharField(choices=[('KGs', 'KGs'), ('Bag', 'Bag')], default='KGs', max_length=10)),
                ('customer', models.CharField(max_length=255)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_gst_included', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('Ordered', 'Ordered'), ('ProductionQueue', 'Production Queue'), ('InProduction', 'In Production'), ('ProductionCompleted', 'Production Completed'), ('Delivered', 'Delivered')], default='Ordered', max_length=30)),
                ('order_instructions', models.TextField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-order_date', '-order_id'],
            },
        ),
    ]
