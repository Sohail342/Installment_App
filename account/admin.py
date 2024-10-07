from django.contrib import admin
from .models import User, Customer

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email','is_admin']

@admin.register(Customer)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email','phone_number']

