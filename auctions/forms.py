from django import forms
from django.core.exceptions import ValidationError

from .models import Auction, Category


class New_listing_form(forms.Form):
    """Creates a Django form to create a new listing. Attrubutes:
      - title(string): The title of the auction.
      - description(string): Description of the auction.
      - starting_bid(float): Mininmum price of the auction."""

    title = forms.CharField(label="Title", max_length=100)
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

    amount = forms.DecimalField(label=False, max_digits=10, decimal_places=2)

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

    content = forms.CharField(label=False, widget=forms.Textarea, max_length=500)