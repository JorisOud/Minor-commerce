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
from .util import render_listing


def index(request, page_title="Active Listings", auctions=None, won_listings=None):
    """Renders a page with a list of auction listings. Has optional parameters for a 
      page title (string), a list of auction listings to be displayed, and a seperate 
      list of won auction listings for the 'my listings' page."""

    if auctions == None:
        auctions = Auction.objects.filter(is_active=True)

    return render(request, "auctions/index.html", {
        "page_title": page_title,
        "auctions": auctions,
        "won_listings": won_listings
    })


def login_view(request):
    """Renders the login view for the auctions app."""

    if request.method != "POST":
        return render(request, "auctions/login.html")

    # Attempt to sign user in
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    # Check if authentication successful
    if user is not None:
        login(request, user)
        return redirect("auctions:index")

    return render(request, "auctions/login.html", {
        "message": "Invalid username and/or password."
    })


def logout_view(request):
    """Logs the user out and redirects to index."""

    logout(request)
    return redirect("auctions:index")


def register(request):
    """Handles the register logic for the auctions app."""

    if request.method != "POST":
       return render(request, "auctions/register.html")

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


def create_listing(request):
    """Renders a page where the user can create a new listing and 
      saves the new listing to the database if it is valid."""

    # if request method is not POST, load create page with empty form
    if request.method != "POST":
        return render(request, "auctions/create_listing.html", {
            "form": New_listing_form()
        })
    
    # if request method is POST, retrieve the form data
    form = New_listing_form(request.POST)

    # if auction is not valid, return to create page with error message
    if not form.is_valid():
        return render(request, "auctions/create_listing.html", {
            "form": form
        })

    # if auction is valid, save auction and redirect to index
    auction = Auction(
        title = form.cleaned_data["title"],
        description = form.cleaned_data["description"],
        starting_bid = form.cleaned_data["starting_bid"],
        current_price = form.cleaned_data["starting_bid"],
        category = Category.objects.get(pk=form.cleaned_data["category"]),
        image = form.cleaned_data["image"],
        creator = request.user
    )
    auction.save()

    return redirect("auctions:index")


def view_listing(request, listing):
    """Renders the page of a listing and handles the logic for adding/deleting
      the listing to/from the user's watchlist and for closing the listing.
      Needs the listing id(string) as parameter."""

    # if method is not post, render listing page
    if request.method != "POST":
        return render_listing(request, listing)

    # if request method is POST, add or remove from watchlist or close listing
    listing_obj = Auction.objects.get(pk=listing)

    if "add" in request.POST:
        request.user.watchlist.add(listing_obj)
        return redirect("auctions:view_listing", listing)
    elif "remove" in request.POST:
        request.user.watchlist.remove(listing_obj)
        return redirect("auctions:view_listing", listing)
    elif "close" in request.POST:
        # set listing to no longer active and appoint winner to auction
        listing_obj.is_active = False
        listing_obj.won_by = listing_obj.auction_bids.last().creator
        listing_obj.save()
        return redirect("auctions:view_listing", listing)


def bid(request, listing):
    """Handles the logic for when the user posts a bid and saves it to the
      database if valid. Needs a listing id(string) for the listing that
      is being bid on as parameter."""

    listing_obj = Auction.objects.get(pk=listing)
    form = Bid_form(request.POST, listing=listing)

    # if bid not valid, return the listing page with error message
    if not form.is_valid():
        return render_listing(request, listing, bid_form=form)

    # if bid is valid, save bid and redirect to listing page
    new_bid = Bid(
        amount = form.cleaned_data["amount"],
        creator = request.user,
        auction = listing_obj
        )
    new_bid.save()

    # update current price
    listing_obj.current_price = form.cleaned_data["amount"]
    listing_obj.save()

    return redirect("auctions:view_listing", listing)


def comment(request, listing):
    """Handles the logic for when the user posts a comment and saves it to the
      database if valid. Needs a listing id(string) for the listing that
      is being commented on as parameter."""

    listing_obj = Auction.objects.get(pk=listing)
    form = Comment_form(request.POST)

    # if comment not valid, return the listing page with error message
    if not form.is_valid():
        return render_listing(request, listing, comment_form=form)

    # if comment is valid, save comment
    new_comment = Comment(
        comment_content = form.cleaned_data["content"],
        creator = request.user,
        auction = listing_obj
        )
    new_comment.save()

    return redirect("auctions:view_listing", listing)


def categories(request):
    """Renders page with a list of all the categories containing links
      to those categories."""

    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category(request, category):
    """Renders a page with all the active listings in a certain category. 
      Needs the category id(string) as parameter."""

    category_obj = Category.objects.get(pk=category)

    return index(request, category_obj.name,
                category_obj.category_auctions.filter(is_active=True))


def watchlist(request):
    """Renders a page with all the listings the user has put on his/her watchlist."""

    return index(request, "Watchlist", request.user.watchlist.all())


def my_listings(request):
    """Renders a page with all the listings the user has created and all the listings 
      the user has won."""

    my_auctions, won_auctions = request.user.auctions.all(), None

    if Auction.objects.filter(won_by=request.user):
        won_auctions = Auction.objects.filter(won_by=request.user)

    return index(request, "Listings you have created", my_auctions, won_auctions)
