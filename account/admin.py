from django.contrib import admin
from .models import User, Customer, Guarantor
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

@admin.register(Guarantor)
class UserAdmin(ModelAdmin):
    list_display = ['name', 'cnic_no','phone_no',]
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ['name', 'email','is_admin']
    search_fields = ('email', 'email')
    list_filter = ['name', 'email']


@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ['first_name', 'last_name', 'cnic',  'email','phone_number']
    search_fields = ('email', 'first_name', 'phone_number', 'cnic')
    list_filter = ['first_name', 'email', 'phone_number']
