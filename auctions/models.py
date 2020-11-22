from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Auction", blank=True)

class Category(models.Model):
    name = models.CharField(max_length=100)

class Auction(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="category_auctions", null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    won_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="won_auctions", null=True, blank=True)

class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_bids")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction_bids")

class Comment(models.Model):
    comment_content = models.CharField(max_length=1000)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comments")


