from django.contrib import admin
from .models import User, Customer

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email','is_admin']
    search_fields = ('email', 'email')
    list_filter = ['name', 'email']


@admin.register(Customer)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email','phone_number']
    search_fields = ('email', 'first_name', 'phone_number')
    list_filter = ['first_name', 'email', 'phone_number']
