from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    path("login", lambda request: HttpResponse("sign in")),
    path("", include("qubesync.django.urls")),
]
