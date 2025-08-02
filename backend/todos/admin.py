from django.contrib import admin
from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'completed', 'priority', 'created_at']
    list_filter = ['completed', 'priority', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['completed', 'priority']
