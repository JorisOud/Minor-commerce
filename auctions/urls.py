from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("categories", views.categories, name="categories"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category/<str:category>", views.category, name="category"),
    path("view_listing/<str:listing>", views.view_listing, name="view_listing"),
    path("bid/<str:listing>", views.bid, name="bid"),
    path("comment/<str:listing>", views.comment, name="comment")
]
