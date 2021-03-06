# Design document
## Application workflow
- Active listings: The user can see what listings are active by clicking the link at the top of the page.
- Categories: the user can go to an overview of all the categories by clicking the link on top of the page.
- The user can go to the category page: a page of all the listings within a certain category, from the Categories page mentioned above.
- Listing page: The user can go to the page of a certain listing from either the active listings page, the page of a certain category or the users watchlist page. 
- The user can go to the login page, the register page, the create auction page and his watchlist page by clicking the link at the top of the page. If the link is visable sometimes depends on whether the user is logged in.

## Models needed for application
- Users
- Auctions
- Bids
- Comments
- Categories
- Watchlist_items

![models](design_images/models.PNG)

## Database info needed per page
- Active listings: all auctions
- Category list: All categories
- Category page: all auctions in that category
- Listing page: that auction info, bids on that auction, comments on that auction
- Login page: users, to check if username and password are valid
- Register page: All users (to check if username is not used yet), auctions(to check if title is not yet used)
- Create auction page: current user, categories (to create dropdown menu)
- Watchlist page: current user, Watchlist_items for that user, auctions that the users watchlist_items correspond with

## Arrow diagram
![arrow diagram](design_images/Commerce_pijltjes.png)
## Active listings
![Active listings](design_images/Active_listings.png)
## Categories
![Category list](design_images/Categories.png)
## Category page
![Category page](design_images/Category_page.png)
## Listing page
![Listing page](design_images/Listing_page.png)
## Login page
![Login page](design_images/Login.png)
## Register page
![Register page](design_images/Register.png)
## Create auction
![Create auction](design_images/New_listing.png)
## Watchlist
![Watchlist page](design_images/Watchlist.png)
