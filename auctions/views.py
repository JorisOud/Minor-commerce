###################################################################
# views.py
#
# Programmeerplatform
# Joris Oud
#
# - Implements the views for the auctions application
###################################################################


from django import forms
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Category, Bid, Comment


class New_listing_form(forms.Form):
    """Creates a Django form to create a new listing. Attrubutes:
      - title(string): The title of the auction.
      - description(string): Description of the auction.
      - starting_bid(float): Mininmum price of the auction."""

    title = forms.CharField(label="Auction Title", max_length=100)
    description = forms.CharField(label="Description", widget=forms.Textarea, max_length=1000)
    starting_bid = forms.DecimalField(label="Starting Bid", max_digits=10, decimal_places=2)
    category = forms.CharField(
        label="Category", 
        widget=forms.Select(choices=Category.objects.values_list("id", "name").distinct()))
    image = forms.URLField(required=False)

class Bid_form(forms.Form):
    """Creates a Django form to place a bid. Attrubutes:
      - amount(float): The amount of the bid.
      keyword argument:
      - listing(string): Id of the listing object that the bid is related to."""

    amount = forms.DecimalField(label="Bid on this item", max_digits=10, decimal_places=2)

    def __init__(self, *args, **kwargs):
        listing = kwargs.pop('listing')
        super(Bid_form, self).__init__(*args, **kwargs)
        self.listing = listing

    def clean_amount(self):
        """Raises a ValidationError if the bid amount is lower than the starting bid
          or lower than or equal to a previous bid."""

        amount = self.cleaned_data["amount"]
        listing_obj = Auction.objects.get(pk=self.listing)

        if listing_obj.auction_bids.last() == None:
            if amount < listing_obj.starting_bid:
                raise ValidationError("Error: Bid is lower than the starting bid.")
        else:
            if amount <= listing_obj.auction_bids.last().amount:
                raise ValidationError("Error: Bid must be higher than the previous bids.")

        return amount

class Comment_form(forms.Form):
    """Creates a Django form to place a comment. Attrubutes:
      - content(string): The content of the comment."""

    content = forms.CharField(label="Place a comment", widget=forms.Textarea, max_length=500)

def index(request, page_title="Active Listings", auctions=None):
    if auctions == None:
        auctions = Auction.objects.all()

    return render(request, "auctions/index.html", {
        "page_title": page_title,
        "auctions": auctions,
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("auctions:index")
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return redirect("auctions:index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect("auctions:index")
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    if request.method != "POST":
        return render(request, "auctions/create_listing.html", {
            "form": New_listing_form()
        })
    
    form = New_listing_form(request.POST)
    if form.is_valid():
        auction = Auction(
            title = form.cleaned_data["title"],
            description = form.cleaned_data["description"],
            starting_bid = form.cleaned_data["starting_bid"],
            current_price= form.cleaned_data["starting_bid"],
            category = Category.objects.get(pk=form.cleaned_data["category"]),
            image = form.cleaned_data["image"],
            creator = request.user
        )
        auction.save()
        return redirect("auctions:index")

    return render(request, "auctions/create_listing.html", {
        "form": form
    })

def bid(request, listing):
    listing_obj = Auction.objects.get(pk=listing)

    if listing_obj in request.user.watchlist.all():
        on_watchlist = True
    else:
        on_watchlist = False

    form = Bid_form(request.POST, listing=listing)
    current_bids = listing_obj.auction_bids.all()
    comments = listing_obj.comments.all()

    if form.is_valid():
        new_bid = Bid(
            amount = form.cleaned_data["amount"],
            creator = request.user,
            auction = listing_obj
            )
        new_bid.save()

        listing_obj.current_price = form.cleaned_data["amount"]
        listing_obj.save()

        return redirect("auctions:view_listing", listing_obj.id)
    else:
        return render(request, "auctions/view_listing.html", {
            "auction": listing_obj,
            "on_watchlist": on_watchlist,
            "bid_form": form,
            "current_bids": current_bids,
            "comment_form": Comment_form(),
            "comments": comments
        })

def comment(request, listing):
    listing_obj = Auction.objects.get(pk=listing)

    if listing_obj in request.user.watchlist.all():
        on_watchlist = True
    else:
        on_watchlist = False

    form = Comment_form(request.POST)
    current_bids = listing_obj.auction_bids.all()
    comments = listing_obj.comments.all()

    if form.is_valid():
        new_comment = Comment(
            comment_content = form.cleaned_data["content"],
            creator = request.user,
            auction = listing_obj
            )
        new_comment.save()
        return redirect("auctions:view_listing", listing_obj.id)
    else:
        return render(request, "auctions/view_listing.html", {
            "auction": listing_obj,
            "on_watchlist": on_watchlist,
            "bid_form": Bid_form(listing=listing),
            "current_bids": current_bids,
            "comment_form": form,
            "comments": comments
        })

def view_listing(request, listing):
    listing_obj = Auction.objects.get(pk=listing)
    if request.method == "POST":
        if "add" in request.POST:
            request.user.watchlist.add(listing_obj)
            return redirect("auctions:view_listing", listing)
        elif "remove" in request.POST:
            request.user.watchlist.remove(listing_obj)
            return redirect("auctions:view_listing", listing)

    if listing_obj in request.user.watchlist.all():
        on_watchlist = True
    else:
        on_watchlist = False

    current_bids = listing_obj.auction_bids.all()
    comments = listing_obj.comments.all()

    return render(request, "auctions/view_listing.html", {
        "auction": listing_obj,
        "on_watchlist": on_watchlist,
        "bid_form": Bid_form(listing=listing),
        "current_bids": current_bids,
        "comment_form": Comment_form(),
        "comments": comments
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def category(request, category):
    category_obj = Category.objects.get(pk=category)
    return index(request, category_obj.name, category_obj.category_auctions.all())

def watchlist(request):
    return index(request, "Watchlist", request.user.watchlist.all())