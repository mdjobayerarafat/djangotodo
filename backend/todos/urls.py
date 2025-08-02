from django.urls import path
from .views import TodoListCreateView, TodoDetailView, TodoToggleView

urlpatterns = [
    path('', TodoListCreateView.as_view(), name='todo-list-create'),
    path('<int:pk>/', TodoDetailView.as_view(), name='todo-detail'),
    path('<int:pk>/toggle/', TodoToggleView.as_view(), name='todo-toggle'),
]
