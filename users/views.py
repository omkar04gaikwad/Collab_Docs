from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def hello(request):
    return HttpResponse("Hello, Google Docs Clone Django Backend!")

from rest_framework import viewsets
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
