from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField()
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="menuitems",
    )

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "menuitem"],
                name="unique_cart_user_menuitem",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.menuitem.title}"


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    delivery_crew = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_orders",
    )
    status = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    menuitem = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.menuitem.title} x {self.quantity}"


class Booking(models.Model):
    """A table reservation made by an authenticated customer."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    name = models.CharField(max_length=100)
    no_of_guests = models.PositiveSmallIntegerField(default=2)
    booking_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["booking_date"]

    def __str__(self):
        return f"{self.name} - {self.booking_date:%Y-%m-%d %H:%M}"
