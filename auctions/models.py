from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Auction", blank=True)

    def __str__(self):
        return f"{self.username}"

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

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

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_bids")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction_bids")

    def __str__(self):
        return f"Bid made by {self.creator.username} on {self.auction.title}"

class Comment(models.Model):
    comment_content = models.CharField(max_length=1000)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Comment made by {self.creator.username} on {self.auction.title}"


