from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from .models import Booking, Category, MenuItem


class LittleLemonWebTests(TestCase):
    def test_homepage_serves_static_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fresh food. Warm welcomes.")
        self.assertContains(response, "/api/menu-items/")


class MenuAPITests(TestCase):
    def setUp(self):
        category = Category.objects.create(title="Starters", slug="starters")
        MenuItem.objects.create(title="Bruschetta", price="8.50", inventory=20, category=category)

    def test_menu_list_is_public(self):
        response = self.client.get("/api/menu-items/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bruschetta")

    def test_menu_item_detail(self):
        item = MenuItem.objects.get(title="Bruschetta")
        response = self.client.get(f"/api/menu-items/{item.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Bruschetta")


class AuthenticationAndBookingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="customer", password="StrongTestPass123!")
        self.client = APIClient()

    def test_user_registration_endpoint(self):
        response = self.client.post("/api/users/", {
            "username": "newcustomer",
            "password": "StrongRegistrationPass123!",
        }, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(User.objects.filter(username="newcustomer").exists())

    def test_booking_requires_authentication(self):
        response = self.client.get("/api/bookings/")
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_create_and_list_booking(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "name": "Test Customer",
            "no_of_guests": 3,
            "booking_date": (timezone.now() + timedelta(days=2)).isoformat(),
        }
        response = self.client.post("/api/bookings/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(Booking.objects.filter(user=self.user).count(), 1)
        list_response = self.client.get("/api/bookings/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data["count"], 1)

    def test_booking_rejects_past_date(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "name": "Test Customer",
            "no_of_guests": 2,
            "booking_date": (timezone.now() - timedelta(days=1)).isoformat(),
        }
        response = self.client.post("/api/bookings/", payload, format="json")
        self.assertEqual(response.status_code, 400)
