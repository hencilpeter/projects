from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marania_invoice_app', '0024_alter_order_piece_weight'),
    ]

    operations = [
        # 1. Add order_key as nullable initially
        migrations.AddField(
            model_name='order',
            name='order_key',
            field=models.IntegerField(null=True, blank=True),
        ),
        # 2. Copy existing order_id values into order_key
        migrations.RunSQL(
            sql="UPDATE marania_invoice_app_order SET order_key = order_id WHERE order_key IS NULL",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # 3. Remove the old order_id AutoField (primary key)
        migrations.RemoveField(
            model_name='order',
            name='order_id',
        ),
        # 4. Add id AutoField as the new primary key
        migrations.AddField(
            model_name='order',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        # 5. Make order_key non-nullable
        migrations.AlterField(
            model_name='order',
            name='order_key',
            field=models.IntegerField(),
        ),
    ]
