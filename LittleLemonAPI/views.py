from decimal import Decimal

from django.contrib.auth.models import Group, User
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, MenuItem, Cart, Order, OrderItem, Booking
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    CartSerializer,
    OrderSerializer,
    UserGroupSerializer,
    BookingSerializer,
)
from .permissions import IsManager, IsManagerOrAdmin


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsManagerOrAdmin()]


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    filterset_fields = ["category"]
    search_fields = ["title", "category__title"]
    ordering_fields = ["price", "title", "inventory"]
    ordering = ["id"]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsManager()]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsManager()]


class ManagerUsersView(generics.ListCreateAPIView):
    serializer_class = UserGroupSerializer

    def get_permissions(self):
        return [IsManagerOrAdmin()]

    def get_queryset(self):
        group, _ = Group.objects.get_or_create(name="Manager")
        return group.user_set.all()

    def create(self, request, *args, **kwargs):
        username = request.data.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        group, _ = Group.objects.get_or_create(name="Manager")
        group.user_set.add(user)

        return Response(
            {"message": f"{username} added to Manager group"},
            status=status.HTTP_201_CREATED,
        )


class ManagerUserDetailView(generics.DestroyAPIView):
    serializer_class = UserGroupSerializer

    def get_permissions(self):
        return [IsManagerOrAdmin()]

    def destroy(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs["pk"])
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        group, _ = Group.objects.get_or_create(name="Manager")
        group.user_set.remove(user)

        return Response(
            {"message": "User removed from Manager group"},
            status=status.HTTP_200_OK,
        )


class DeliveryCrewUsersView(generics.ListCreateAPIView):
    serializer_class = UserGroupSerializer

    def get_permissions(self):
        return [IsManager()]

    def get_queryset(self):
        group, _ = Group.objects.get_or_create(name="Delivery crew")
        return group.user_set.all()

    def create(self, request, *args, **kwargs):
        username = request.data.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        group, _ = Group.objects.get_or_create(name="Delivery crew")
        group.user_set.add(user)

        return Response(
            {"message": f"{username} added to Delivery crew"},
            status=status.HTTP_201_CREATED,
        )


class DeliveryCrewUserDetailView(generics.DestroyAPIView):
    serializer_class = UserGroupSerializer

    def get_permissions(self):
        return [IsManager()]

    def destroy(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs["pk"])
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        group, _ = Group.objects.get_or_create(name="Delivery crew")
        group.user_set.remove(user)

        return Response(
            {"message": "User removed from Delivery crew"},
            status=status.HTTP_200_OK,
        )


class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    filterset_fields = ["status", "delivery_crew"]
    search_fields = ["user__username", "delivery_crew__username"]
    ordering_fields = ["total", "date", "status"]
    ordering = ["-date"]

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.groups.filter(name="Manager").exists():
            return Order.objects.all()

        if user.groups.filter(name="Delivery crew").exists():
            return Order.objects.filter(delivery_crew=user)

        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response(
                {"message": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = sum(
            (item.price for item in cart_items),
            Decimal("0.00"),
        )

        order = Order.objects.create(
            user=request.user,
            total=total,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )

        cart_items.delete()

        return Response(
            self.get_serializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.groups.filter(name="Manager").exists():
            return Order.objects.all()

        if user.groups.filter(name="Delivery crew").exists():
            return Order.objects.filter(delivery_crew=user)

        return Order.objects.filter(user=user)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user

        is_manager = (
            user.is_staff
            or user.groups.filter(name="Manager").exists()
        )
        is_crew = user.groups.filter(name="Delivery crew").exists()

        if is_crew:
            if order.delivery_crew_id != user.id:
                return Response(
                    {"message": "Not authorized"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if set(request.data.keys()) - {"status"}:
                return Response(
                    {"message": "Delivery crew can only update status"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if "status" not in request.data:
                return Response(
                    {"status": ["This field is required."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            order.status = request.data["status"]
            order.save(update_fields=["status"])

            return Response(
                self.get_serializer(order).data,
                status=status.HTTP_200_OK,
            )

        if is_manager:
            if "delivery_crew" in request.data:
                crew_id = request.data["delivery_crew"]
                try:
                    crew = User.objects.get(id=crew_id)
                except User.DoesNotExist:
                    return Response(
                        {"message": "Delivery crew not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                if not crew.groups.filter(
                    name="Delivery crew"
                ).exists():
                    return Response(
                        {"message": "User is not delivery crew"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                order.delivery_crew = crew

            if "status" in request.data:
                order.status = request.data["status"]

            order.save()

            return Response(
                self.get_serializer(order).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "Not authorized"},
            status=status.HTTP_403_FORBIDDEN,
        )

    def destroy(self, request, *args, **kwargs):
        user = request.user

        if not (
            user.is_staff
            or user.groups.filter(name="Manager").exists()
        ):
            return Response(
                {"message": "Not authorized"},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = self.get_object()
        order.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class BookingListCreateView(generics.ListCreateAPIView):
    """Customers can create reservations and see only their own bookings."""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
