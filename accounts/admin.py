from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'email')
    
    # Какие поля показывать при редактировании
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {'fields': ('phone',)}),
    )
    
    # Какие поля показывать при создании нового пользователя
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительные поля', {'fields': ('email', 'phone')}),
    )