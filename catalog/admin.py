from django.contrib import admin
from .models import SampleCatalog, CatalogType


class CatalogFilter(admin.SimpleListFilter):
    title = 'Activity'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('Active', ('Active')),
            ('Inactive', ('Inactive')),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "Active":
            return queryset.filter(is_active=True)
        elif value == "Inactive":
            return queryset.filter(is_active=False)
        else:
            return queryset


class SampleCatalogAdmin(admin.ModelAdmin):
    list_filter = [CatalogFilter]
    list_display = ('name', 'is_active','catalog_type')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('name', 'catalog_type')


class CatalogTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'express_id','catalog_url')
    search_fields = ('name',)


admin.site.register(SampleCatalog, SampleCatalogAdmin)
admin.site.register(CatalogType, CatalogTypeAdmin)