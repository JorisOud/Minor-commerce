# Generated by Django 3.1.3 on 2020-11-16 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20201116_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(blank=True, to='auctions.Auction'),
        ),
        migrations.AlterField(
            model_name='auction',
            name='category',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_auctions', to='auctions.category'),
        ),
        migrations.DeleteModel(
            name='Watchlist_item',
        ),
    ]
