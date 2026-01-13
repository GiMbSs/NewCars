from django.contrib import admin
from cars.models import Car, Brand

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('model', 'brand', 'factory_year', 'model_year', 'color', 'mileage', 'price', 'is_available', 'created_at', 'updated_at')
    list_filter = ('brand', 'factory_year', 'model_year', 'is_available')
    search_fields = ('model', 'brand', 'color', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        obj._log_user = request.user
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        obj._log_user = request.user
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj._log_user = request.user
            obj.delete()

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
