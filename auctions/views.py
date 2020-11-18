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
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
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
    """Creates a Django form to create a new listing. Attrubutes:
      - amount(float): The amount of the bid."""

    amount = forms.DecimalField(label="Bid on this item", max_digits=10, decimal_places=2)

def index(request, page_title="Active Listings", auctions=Auction.objects.all()):
    return render(request, "auctions/index.html", {
        "page_title": page_title,
        "auctions": auctions
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
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
            category = Category.objects.get(pk=form.cleaned_data["category"]),
            image = form.cleaned_data["image"],
            creator = request.user
        )
        auction.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create_listing.html", {
        "form": form
    })



def bid(request, listing):
    listing_obj = Auction.objects.get(pk=listing)

    if listing_obj in request.user.watchlist.all():
        on_watchlist = True
    else:
        on_watchlist = False

    form = Bid_form(request.POST)

    if form.is_valid():
        new_bid = Bid(
            amount = form.cleaned_data["amount"],
            creator = request.user,
            auction = listing_obj
            )
        new_bid.save()
        return HttpResponseRedirect(reverse("view_listing", args=[listing_obj.id]))
    else:
        return render(request, "auctions/view_listing.html", {
            "auction": listing_obj,
            "on_watchlist": on_watchlist,
            "bid_form": form
        })

def view_listing(request, listing):
    listing_obj = Auction.objects.get(pk=listing)
    if request.method == "POST":
        if "add" in request.POST:
            request.user.watchlist.add(listing_obj)
            return HttpResponseRedirect(reverse("view_listing", args=[listing]))
        elif "remove" in request.POST:
            request.user.watchlist.remove(listing_obj)
            return HttpResponseRedirect(reverse("view_listing", args=[listing]))

    if listing_obj in request.user.watchlist.all():
        on_watchlist = True
    else:
        on_watchlist = False

    current_bids = listing_obj.auction_bids.all()

    return render(request, "auctions/view_listing.html", {
        "auction": listing_obj,
        "on_watchlist": on_watchlist,
        "bid_form": Bid_form(),
        "current_bids": current_bids
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