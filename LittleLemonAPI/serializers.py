from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Category, MenuItem, Cart, Order, OrderItem, Booking


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "inventory", "category"]
        extra_kwargs = {
            "price": {"min_value": 2},
            "inventory": {"min_value": 0},
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "id", "user", "menuitem", "quantity",
            "unit_price", "price"
        ]
        read_only_fields = ["user", "unit_price", "price"]
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=["user", "menuitem"],
            )
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        menuitem = validated_data["menuitem"]
        quantity = validated_data["quantity"]
        unit_price = menuitem.price
        price = unit_price * quantity

        return Cart.objects.create(
            user=user,
            menuitem=menuitem,
            quantity=quantity,
            unit_price=unit_price,
            price=price,
        )


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "menuitem", "quantity", "unit_price", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "user", "delivery_crew", "status",
            "total", "date", "items"
        ]
        read_only_fields = ["user", "total", "date", "items"]


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "name", "no_of_guests", "booking_date", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_no_of_guests(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError("Guest count must be between 1 and 20.")
        return value

    def validate_booking_date(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Booking date must be in the future.")
        return value
