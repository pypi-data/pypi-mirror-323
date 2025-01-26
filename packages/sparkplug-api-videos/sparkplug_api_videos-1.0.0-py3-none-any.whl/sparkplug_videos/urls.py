# django
from django.urls import include, path

# contrib
from rest_framework.routers import SimpleRouter

# app
from . import views


router = SimpleRouter()


router.register(
    prefix=r"videos",
    viewset=views.Video,
    basename="videos",
)


urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]
