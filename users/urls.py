from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)

urlpatterns = [
    path('hello/', views.hello, name='hello'),
    path("", include(router.urls)),
]