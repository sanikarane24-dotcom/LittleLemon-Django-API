from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("LittleLemonAPI.urls")),
    path("api/", include("djoser.urls")),
    path("api/", include("djoser.urls.authtoken")),
]
