from django.urls import path

from .views import (
    CategoryListView,
    MenuItemsView,
    SingleMenuItemView,
    ManagerUsersView,
    ManagerUserDetailView,
    DeliveryCrewUsersView,
    DeliveryCrewUserDetailView,
    CartView,
    OrdersView,
    OrderDetailView,
    BookingListCreateView,
    BookingDetailView,
)

urlpatterns = [
    path("categories/", CategoryListView.as_view()),

    path("menu-items/", MenuItemsView.as_view()),
    path("menu-items/<int:pk>/", SingleMenuItemView.as_view()),

    path("groups/manager/users/", ManagerUsersView.as_view()),
    path(
        "groups/manager/users/<int:pk>/",
        ManagerUserDetailView.as_view(),
    ),

    path(
        "groups/delivery-crew/users/",
        DeliveryCrewUsersView.as_view(),
    ),
    path(
        "groups/delivery-crew/users/<int:pk>/",
        DeliveryCrewUserDetailView.as_view(),
    ),

    path("cart/menu-items/", CartView.as_view()),

    path("orders/", OrdersView.as_view()),
    path("orders/<int:pk>/", OrderDetailView.as_view()),

    path("bookings/", BookingListCreateView.as_view()),
    path("bookings/<int:pk>/", BookingDetailView.as_view()),
]
