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

from .models import User, Auction


class New_listing_form(forms.Form):
    """Creates a Django form to create a new wiki page. Attrubutes:
      - title(string): The title of the auction.
      - description(string): Description of the auction.
      - starting_bid(float): Mininmum price of the auction."""

    title = forms.CharField(label="Auction Title", max_length=100)
    description = forms.CharField(label="Description", widget=forms.Textarea, max_length=1000)
    starting_bid = forms.DecimalField(label="Starting Bid", max_digits=10, decimal_places=2)


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.all()
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
            creator = request.user
        )
        auction.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create_listing.html", {
        "form": form
    })
