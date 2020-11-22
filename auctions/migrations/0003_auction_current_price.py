# Generated by Django 3.1.3 on 2020-11-21 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auction_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='current_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
