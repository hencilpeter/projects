from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('marania_invoice_app', '0112_pricelistconfiguration_mesh_label_overrides'),
    ]
    operations = [
        migrations.CreateModel(
            name='AdHocColourConfiguration',
            fields=[
                ('adhoc_key', models.AutoField(primary_key=True)),
                ('base_colour', models.CharField(max_length=50)),
                ('label', models.CharField(blank=True, default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Ad-hoc Colour Configuration',
                'verbose_name_plural': 'Ad-hoc Colour Configurations',
                'ordering': ['-created_at'],
            },
        ),
    ]
