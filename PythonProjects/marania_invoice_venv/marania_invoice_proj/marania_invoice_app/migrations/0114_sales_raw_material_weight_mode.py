from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('marania_invoice_app', '0113_adhoccolourconfiguration'),
    ]
    operations = [
        migrations.AddField(
            model_name='sales',
            name='raw_material_weight_mode',
            field=models.CharField(blank=True, default='init', help_text='Weight basis for Actual Raw Material Cost: init or proc', max_length=10, null=True),
        ),
    ]
