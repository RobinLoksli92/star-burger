# Generated by Django 3.2 on 2022-07-18 13:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_orderingproduct_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderingproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена'),
        ),
    ]
