from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.authtoken.models import Token


@api_view(['POST'])
def user_registration_view(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "User registration successful. Please explore our app to engage with communities",
            "token": token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful. See what is going on with your family and friends.",
                "token": token.key
            }, status=status.HTTP_200_OK)
        return Response({"error": "Username Or Password is incorrect."}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
