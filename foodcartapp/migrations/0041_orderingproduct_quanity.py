# Generated by Django 3.2 on 2022-07-08 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_alter_order_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderingproduct',
            name='quanity',
            field=models.IntegerField(default=0, verbose_name='Количество'),
            preserve_default=False,
        ),
    ]
