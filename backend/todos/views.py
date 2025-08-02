from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
import json

from .models import Todo
from .serializers import TodoSerializer


class AuthMixin:
    """Mixin to handle JWT authentication for async views"""
    
    async def get_authenticated_user(self, request):
        """Get authenticated user from JWT token"""
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None, JsonResponse({'error': 'Authentication required'}, status=401)
        
        token = auth_header.split(' ')[1]
        
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()
            validated_token = await sync_to_async(jwt_auth.get_validated_token)(token)
            user = await sync_to_async(jwt_auth.get_user)(validated_token)
            return user, None
        except Exception as e:
            return None, JsonResponse({'error': f'Invalid token: {str(e)}'}, status=401)


@method_decorator(csrf_exempt, name='dispatch')
class TodoListCreateView(View, AuthMixin):
    async def get(self, request):
        try:
            # Authenticate user
            user, error_response = await self.get_authenticated_user(request)
            if error_response:
                return error_response
            
            # Get todos asynchronously
            todos = await sync_to_async(list)(
                Todo.objects.filter(user=user).order_by('-created_at')
            )
            
            # Serialize data
            serializer_data = await sync_to_async(lambda: TodoSerializer(todos, many=True).data)()
            
            return JsonResponse(serializer_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    async def post(self, request):
        try:
            # Authenticate user
            user, error_response = await self.get_authenticated_user(request)
            if error_response:
                return error_response
            
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))
            
            # Validate and save
            serializer = TodoSerializer(data=data, context={'request': type('Request', (), {'user': user})()})
            is_valid = await sync_to_async(serializer.is_valid)()
            if is_valid:
                todo = await sync_to_async(serializer.save)()
                todo_data = await sync_to_async(lambda: TodoSerializer(todo).data)()
                return JsonResponse(todo_data, status=201)
            else:
                errors = await sync_to_async(lambda: serializer.errors)()
                return JsonResponse(errors, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TodoDetailView(View, AuthMixin):
    async def get_object(self, pk, user):
        return await sync_to_async(get_object_or_404)(Todo, pk=pk, user=user)

    async def get(self, request, pk):
        try:
            # Authenticate user
            user, error_response = await self.get_authenticated_user(request)
            if error_response:
                return error_response
            
            todo = await self.get_object(pk, user)
            todo_data = await sync_to_async(lambda: TodoSerializer(todo).data)()
            return JsonResponse(todo_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=404)

    async def put(self, request, pk):
        try:
            # Authenticate user
            user, error_response = await self.get_authenticated_user(request)
            if error_response:
                return error_response
            
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))
            
            todo = await self.get_object(pk, user)
            serializer = TodoSerializer(todo, data=data, partial=True)
            is_valid = await sync_to_async(serializer.is_valid)()
            if is_valid:
                updated_todo = await sync_to_async(serializer.save)()
                todo_data = await sync_to_async(lambda: TodoSerializer(updated_todo).data)()
                return JsonResponse(todo_data)
            else:
                errors = await sync_to_async(lambda: serializer.errors)()
                return JsonResponse(errors, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=404)

    async def delete(self, request, pk):
        try:
            # Authenticate user
            user, error_response = await self.get_authenticated_user(request)
            if error_response:
                return error_response
            
            todo = await self.get_object(pk, user)
            await sync_to_async(todo.delete)()
            return JsonResponse({}, status=204)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class TodoToggleView(View, AuthMixin):
    async def patch(self, request, pk):
        try:
            # Authenticate user
            user, error_response = await self.get_authenticated_user(request)
            if error_response:
                return error_response
            
            todo = await sync_to_async(get_object_or_404)(Todo, pk=pk, user=user)
            todo.completed = not todo.completed
            await sync_to_async(todo.save)()
            todo_data = await sync_to_async(lambda: TodoSerializer(todo).data)()
            return JsonResponse(todo_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=404)
