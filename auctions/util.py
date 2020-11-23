from django.shortcuts import render

from .forms import Bid_form, Comment_form
from .models import Auction


def render_listing(request, listing, bid_form=None, comment_form=Comment_form()):
    listing_obj = Auction.objects.get(pk=listing)

    if bid_form == None:
        bid_form = Bid_form(listing=listing)

    on_watchlist, own_listing, listing_won = False, False, False

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
        "bid_form": bid_form,
        "current_bids": current_bids,
        "comment_form": comment_form,
        "comments": comments
    })
