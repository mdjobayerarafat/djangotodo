from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import sync_to_async, async_to_sync
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import asyncio

from .models import Todo
from .serializers import TodoSerializer


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
class TodoListCreateView(AsyncAPIView):
    permission_classes = [IsAuthenticated]

    async def get(self, request):
        # Get todos for the user
        todos = await sync_to_async(list)(
            Todo.objects.filter(user=request.user).order_by('-created_at')
        )
        
        # Serialize data
        serializer_data = await sync_to_async(lambda: TodoSerializer(todos, many=True).data)()
        return Response(serializer_data)

    async def post(self, request):
        serializer = TodoSerializer(data=request.data, context={'request': request})
        
        # Check if serializer is valid
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            # Save todo
            todo = await sync_to_async(serializer.save)()
            
            # Get todo data
            todo_data = await sync_to_async(lambda: TodoSerializer(todo).data)()
            return Response(todo_data, status=status.HTTP_201_CREATED)
        
        # Get errors
        errors = await sync_to_async(lambda: serializer.errors)()
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TodoDetailView(AsyncAPIView):
    permission_classes = [IsAuthenticated]

    async def get_object(self, pk, user):
        return await sync_to_async(get_object_or_404)(Todo, pk=pk, user=user)

    async def get(self, request, pk):
        todo = await self.get_object(pk, request.user)
        
        # Serialize data
        serializer_data = await sync_to_async(lambda: TodoSerializer(todo).data)()
        return Response(serializer_data)

    async def put(self, request, pk):
        todo = await self.get_object(pk, request.user)
        serializer = TodoSerializer(todo, data=request.data, partial=True)
        
        # Check if serializer is valid
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            # Save todo
            updated_todo = await sync_to_async(serializer.save)()
            
            # Get todo data
            todo_data = await sync_to_async(lambda: TodoSerializer(updated_todo).data)()
            return Response(todo_data)
        
        # Get errors
        errors = await sync_to_async(lambda: serializer.errors)()
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    async def delete(self, request, pk):
        todo = await self.get_object(pk, request.user)
        await sync_to_async(todo.delete)()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_exempt, name='dispatch')
class TodoToggleView(AsyncAPIView):
    permission_classes = [IsAuthenticated]

    async def patch(self, request, pk):
        todo = await sync_to_async(get_object_or_404)(Todo, pk=pk, user=request.user)
        
        # Toggle completion status
        todo.completed = not todo.completed
        await sync_to_async(todo.save)()
        
        # Get todo data
        serializer_data = await sync_to_async(lambda: TodoSerializer(todo).data)()
        return Response(serializer_data)
