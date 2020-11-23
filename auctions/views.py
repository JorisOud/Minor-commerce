###################################################################
# views.py
#
# Programmeerplatform
# Joris Oud
#
# - Implements the views for the auctions application
###################################################################


from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import New_listing_form, Bid_form, Comment_form
from .models import User, Auction, Category, Bid, Comment


def index(request, page_title="Active Listings", auctions=None, won_listings=None):
    if auctions == None:
        auctions = Auction.objects.filter(is_active=True)

    return render(request, "auctions/index.html", {
        "page_title": page_title,
        "auctions": auctions,
        "won_listings": won_listings
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
        elif "close" in request.POST:
            listing_obj.is_active = False
            listing_obj.won_by = listing_obj.auction_bids.last().creator
            listing_obj.save()
            return redirect("auctions:view_listing", listing)

    on_watchlist = False
    own_listing = False
    listing_won = False

    if listing_obj in request.user.watchlist.all():
        on_watchlist = True
 
    if listing_obj.creator == request.user:
        own_listing = True

    if listing_obj.auction_bids.all():
        if listing_obj.auction_bids.last().creator == request.user:
            listing_won =True

    current_bids = listing_obj.auction_bids.all()
    comments = listing_obj.comments.all()

    return render(request, "auctions/view_listing.html", {
        "auction": listing_obj,
        "on_watchlist": on_watchlist,
        "own_listing": own_listing,
        "listing_won": listing_won,
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
    return index(request, category_obj.name, category_obj.category_auctions.filter(is_active=True))

def watchlist(request):
    return index(request, "Watchlist", request.user.watchlist.all())

def my_listings(request):
    my_auctions = request.user.auctions.all()
    won_auctions = None
    if Auction.objects.filter(won_by=request.user):
        won_auctions = Auction.objects.filter(won_by=request.user)
    # my_auctions |= Auction.objects.filter(won_by=request.user)
    return index(request, "Listings you have created", my_auctions, won_auctions)
