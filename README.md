# Little Lemon Restaurant — Django + REST API

A peer-review-ready Django project with a rendered HTML homepage, REST APIs for menu items and table bookings, user registration/authentication, role-aware menu/cart/order endpoints, unit tests, and MySQL configuration.

## Requirements
- Python 3.10+
- MySQL Server (for the MySQL assignment requirement)
- Git

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create a MySQL database:

```sql
CREATE DATABASE littlelemon CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Set the environment variables shown in `.env.example` in your terminal. Django does not automatically load `.env`, so export/set them in your shell (or use your preferred environment-variable loader). If `DB_NAME` is not set, the project uses SQLite for a quick local run; set `DB_NAME=littlelemon` to enable the MySQL backend.

PowerShell example:
```powershell
$env:DB_NAME='littlelemon'
$env:DB_USER='root'
$env:DB_PASSWORD='your_mysql_password'
$env:DB_HOST='127.0.0.1'
$env:DB_PORT='3306'
```

Then run:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/ for the HTML homepage and http://127.0.0.1:8000/admin/ for Django admin.

## Main endpoints
All endpoints use `/api/` as the base path. API routes accept trailing slashes.

| Purpose | Method | Endpoint | Access |
|---|---|---|---|
| Categories | GET | `/api/categories/` | Public |
| Menu list/create | GET, POST | `/api/menu-items/` | Read public; create Manager only |
| Menu item detail | GET, PUT, PATCH, DELETE | `/api/menu-items/<id>/` | Read public; changes Manager only |
| Register user | POST | `/api/users/` | Public registration (Djoser) |
| Get auth token | POST | `/api/token/login/` | Username/password |
| Logout/revoke token | POST | `/api/token/logout/` | Authenticated |
| Table bookings | GET, POST | `/api/bookings/` | Authenticated; own bookings only |
| Booking detail | GET, PUT, PATCH, DELETE | `/api/bookings/<id>/` | Authenticated; own bookings only |
| Cart | GET, POST, DELETE | `/api/cart/menu-items/` | Authenticated |
| Orders | GET, POST | `/api/orders/` | Authenticated; role-aware |
| Manager group | GET, POST | `/api/groups/manager/users/` | Manager/admin |
| Delivery crew group | GET, POST | `/api/groups/delivery-crew/users/` | Manager |

Menu supports filtering by category, search by title/category, ordering by price/title/inventory, and page-number pagination. DRF browsable API is enabled for browser-based testing.

## Test with Insomnia
1. Start the server and create a user with `POST http://127.0.0.1:8000/api/users/` and JSON such as `{"username":"customer1","password":"StrongPass123!"}`.
2. Obtain a token with `POST http://127.0.0.1:8000/api/token/login/`, JSON `{"username":"customer1","password":"StrongPass123!"}`.
3. For protected routes, add header `Authorization: Token <token>`.
4. Test `GET /api/menu-items/` without a token.
5. Test `POST /api/bookings/` with JSON, for example:
```json
{
  "name": "Customer One",
  "no_of_guests": 2,
  "booking_date": "2027-01-15T19:00:00+05:30"
}
```
Use a future datetime. Then test `GET /api/bookings/` and `GET /api/bookings/1/`.

Registration endpoint details can also be checked through Djoser's API. Create an admin user with `createsuperuser` and assign users to `Manager` or `Delivery crew` groups in Django admin to test role-based permissions.

## Run unit tests
```bash
python manage.py test
```
Tests cover HTML rendering, public menu retrieval, menu detail, authentication protection for bookings, booking creation/listing, and rejection of past booking dates.

## GitHub submission
```bash
git init
git add .
git commit -m "Complete Little Lemon Django project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```
Replace the remote URL with your own GitHub repository. Do not commit passwords or a real `.env` file.
