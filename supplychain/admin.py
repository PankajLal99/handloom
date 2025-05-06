from django.contrib import admin
from .models import Weaver, Loom, ThreadBatch, ProductionLog

@admin.register(Weaver)
class WeaverAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'skill_level', 'created_at')
    search_fields = ('name', 'contact')
    list_filter = ('skill_level',)

@admin.register(Loom)
class LoomAdmin(admin.ModelAdmin):
    list_display = ('loom_id', 'assigned_weaver', 'status', 'created_at')
    search_fields = ('loom_id', 'assigned_weaver__name')
    list_filter = ('status',)

@admin.register(ThreadBatch)
class ThreadBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_code', 'date', 'color', 'quantity_kg', 'created_by')
    search_fields = ('batch_code', 'color')
    list_filter = ('date',)

@admin.register(ProductionLog)
class ProductionLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'loom', 'thread_batch', 'meters_produced', 'created_by')
    search_fields = ('loom__loom_id', 'thread_batch__batch_code')
    list_filter = ('date', 'loom')
