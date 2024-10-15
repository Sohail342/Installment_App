from django.contrib import admin
from . models import Product, Category
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

@admin.register(Category)
class ProductAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ['id', 'name', 'category_moto', 'date']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ['id','name', 'price', 'inventory' ,'category']
    search_fields = ['name']
    list_filter = ('name',)