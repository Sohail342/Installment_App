from django.contrib import admin
from . models import Product, Category
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

@admin.register(Category)
class ProductAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ['name', 'category_moto', 'date']
    exclude = ['slug']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ['name', 'price', 'inventory' ,'category']
    exclude = ['down_payment_3_months', 'down_payment_6_months', 'down_payment_9_months', 'down_payment_12_months', 'fee_3_months', 'fee_6_months', 'fee_9_months', 'fee_12_months']
    search_fields = ['name']
    list_filter = ('name',)