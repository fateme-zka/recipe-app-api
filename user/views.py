from django.shortcuts import render
from .serializers import AuthTokenSerializer, UserSerializer

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings, APISettings
from rest_framework import generics


class CreateUserView(generics.CreateAPIView):
    """Create a new user in system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
