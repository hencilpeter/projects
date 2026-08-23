from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marania_invoice_app', '0086_rename_small_size_cost_per_kg_processingcost_small_depth_size_cost_per_kg_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pricelistconfiguration',
            old_name='colour_price',
            new_name='colour_price_per_kg',
        ),
        migrations.RenameField(
            model_name='pricelistconfiguration',
            old_name='small_mesh_size',
            new_name='additional_cost_starting_depth_md',
        ),
        migrations.RenameField(
            model_name='pricelistconfiguration',
            old_name='small_mesh_price',
            new_name='small_mesh_depth_price_per_kg',
        ),
        migrations.AddField(
            model_name='pricelistconfiguration',
            name='processing_cost_per_kg',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='pricelistconfiguration',
            name='additional_cost_per_kg',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
