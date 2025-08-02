from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from asgiref.sync import sync_to_async, async_to_sync
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import asyncio

from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer


class AsyncAPIView(APIView):
    """Custom APIView that properly handles async methods"""
    
    def dispatch(self, request, *args, **kwargs):
        # Get the handler method
        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        
        # If it's an async method, run it in sync context
        if asyncio.iscoroutinefunction(handler):
            return async_to_sync(handler)(request, *args, **kwargs)
        else:
            return handler(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(AsyncAPIView):
    permission_classes = [AllowAny]

    async def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        # Check if serializer is valid
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            # Save user
            user = await sync_to_async(serializer.save)()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Get user data
            user_data = await sync_to_async(lambda: UserSerializer(user).data)()
            
            return Response({
                'message': 'User created successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data
            }, status=status.HTTP_201_CREATED)
        
        # Get errors
        errors = await sync_to_async(lambda: serializer.errors)()
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(AsyncAPIView):
    permission_classes = [AllowAny]

    async def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        # Check if serializer is valid
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # Authenticate user
            user = await sync_to_async(authenticate)(username=username, password=password)
            
            if user:
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                # Get user data
                user_data = await sync_to_async(lambda: UserSerializer(user).data)()
                
                return Response({
                    'message': 'Login successful',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': user_data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get errors
        errors = await sync_to_async(lambda: serializer.errors)()
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(AsyncAPIView):
    permission_classes = [IsAuthenticated]

    async def get(self, request):
        # Get user data
        user_data = await sync_to_async(lambda: UserSerializer(request.user).data)()
        return Response(user_data)

    async def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        
        # Check if serializer is valid
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            # Save user
            user = await sync_to_async(serializer.save)()
            
            # Get user data
            user_data = await sync_to_async(lambda: UserSerializer(user).data)()
            return Response(user_data)
        
        # Get errors
        errors = await sync_to_async(lambda: serializer.errors)()
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
