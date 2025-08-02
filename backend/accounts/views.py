from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from asgiref.sync import sync_to_async
import json

from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    async def post(self, request):
        try:
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))
            
            # Validate data
            serializer = UserRegistrationSerializer(data=data)
            is_valid = await sync_to_async(serializer.is_valid)()
            
            if is_valid:
                # Create user asynchronously
                user = await sync_to_async(serializer.save)()
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                # Serialize user data
                user_data = await sync_to_async(lambda: UserSerializer(user).data)()
                
                return JsonResponse({
                    'message': 'User created successfully',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': user_data
                }, status=201)
            else:
                errors = await sync_to_async(lambda: serializer.errors)()
                return JsonResponse(errors, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    async def post(self, request):
        try:
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))
            
            # Validate data
            serializer = UserLoginSerializer(data=data)
            is_valid = await sync_to_async(serializer.is_valid)()
            
            if is_valid:
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                
                # Authenticate user
                user = await sync_to_async(authenticate)(username=username, password=password)
                
                if user:
                    # Generate tokens
                    refresh = RefreshToken.for_user(user)
                    
                    # Serialize user data
                    user_data = await sync_to_async(lambda: UserSerializer(user).data)()
                    
                    return JsonResponse({
                        'message': 'Login successful',
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': user_data
                    }, status=200)
                else:
                    return JsonResponse({
                        'error': 'Invalid credentials'
                    }, status=401)
            else:
                errors = await sync_to_async(lambda: serializer.errors)()
                return JsonResponse(errors, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ProfileView(View):
    async def get(self, request):
        try:
            # Check authentication
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            token = auth_header.split(' ')[1]
            
            # Validate token and get user
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()
            
            try:
                validated_token = await sync_to_async(jwt_auth.get_validated_token)(token)
                user = await sync_to_async(jwt_auth.get_user)(validated_token)
                
                # Serialize user data
                user_data = await sync_to_async(lambda: UserSerializer(user).data)()
                return JsonResponse(user_data)
                
            except Exception:
                return JsonResponse({'error': 'Invalid token'}, status=401)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    async def put(self, request):
        try:
            # Check authentication
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            token = auth_header.split(' ')[1]
            
            # Validate token and get user
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()
            
            try:
                validated_token = await sync_to_async(jwt_auth.get_validated_token)(token)
                user = await sync_to_async(jwt_auth.get_user)(validated_token)
                
                # Parse JSON data
                data = json.loads(request.body.decode('utf-8'))
                
                # Update user
                serializer = UserSerializer(user, data=data, partial=True)
                is_valid = await sync_to_async(serializer.is_valid)()
                if is_valid:
                    updated_user = await sync_to_async(serializer.save)()
                    user_data = await sync_to_async(lambda: UserSerializer(updated_user).data)()
                    return JsonResponse(user_data)
                else:
                    errors = await sync_to_async(lambda: serializer.errors)()
                    return JsonResponse(errors, status=400)
                    
            except Exception:
                return JsonResponse({'error': 'Invalid token'}, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
