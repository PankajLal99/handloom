from django.urls import path
from . import views

app_name = 'supplychain'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('weavers/', views.weaver_list, name='weaver_list'),
    path('weavers/add/', views.weaver_create, name='weaver_create'),
    path('weavers/<int:pk>/', views.weaver_detail, name='weaver_detail'),
    path('weavers/<int:pk>/edit/', views.weaver_edit, name='weaver_edit'),
    path('weavers/<int:pk>/delete/', views.weaver_delete, name='weaver_delete'),
    
    path('looms/', views.loom_list, name='loom_list'),
    path('looms/add/', views.loom_create, name='loom_create'),
    path('looms/<str:loom_id>/', views.loom_detail, name='loom_detail'),
    path('looms/<str:loom_id>/edit/', views.loom_edit, name='loom_edit'),
    path('looms/<str:loom_id>/delete/', views.loom_delete, name='loom_delete'),
    path('looms/<str:loom_id>/assignment/', views.loom_assignment_edit, name='loom_assignment'),
    
    path('production/', views.production_list, name='production_list'),
    path('production/add/', views.production_create, name='production_create'),
    path('production/<int:pk>/', views.production_detail, name='production_detail'),
    path('production/<int:pk>/edit/', views.production_edit, name='production_edit'),
    path('production/<int:pk>/delete/', views.production_delete, name='production_delete'),
    
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_create, name='inventory_create'),
    path('inventory/<int:pk>/', views.inventory_detail, name='inventory_detail'),
    path('inventory/<int:pk>/edit/', views.inventory_edit, name='inventory_edit'),
    path('inventory/<int:pk>/delete/', views.inventory_delete, name='inventory_delete'),
    
    path('thread-batches/', views.thread_batch_list, name='thread_batch_list'),
    path('thread-batches/add/', views.thread_batch_create, name='thread_batch_create'),
    path('thread-batches/<int:pk>/', views.thread_batch_detail, name='thread_batch_detail'),
    path('thread-batches/<int:pk>/edit/', views.thread_batch_edit, name='thread_batch_edit'),
    path('thread-batches/<int:pk>/delete/', views.thread_batch_delete, name='thread_batch_delete'),
    
    path('production/', views.production_list, name='production_list'),
    path('production/create/', views.production_create, name='production_create'),
    path('loom-assignments/', views.loom_assignments, name='loom_assignments'),
    path('loom-assignments/<str:loom_id>/edit/', views.loom_assignment_edit, name='loom_assignment_edit'),
    
    # Analytics URLs
    path('analytics/weaver-performance/', views.weaver_performance, name='weaver_performance'),
    path('analytics/top-looms/', views.top_looms, name='top_looms'),
    path('analytics/production-trends/', views.production_trends, name='production_trends'),
    path('analytics/inventory-status/', views.inventory_status, name='inventory_status'),
    path('analytics/thread-utilization/', views.thread_utilization, name='thread_utilization'),
    path('analytics/low-production/', views.low_production_alerts, name='low_production_alerts'),
    path('analytics/thread-consumption/', views.thread_consumption_report, name='thread_consumption_report'),
    path('analytics/production-heatmap/', views.production_heatmap, name='production_heatmap'),
    path('analytics/loom-efficiency/', views.loom_efficiency, name='loom_efficiency'),
    path('analytics/tracking/', views.tracking_analytics, name='tracking_analytics'),
    
    # Export URLs
    path('export/production-logs/', views.export_production_logs, name='export_production_logs'),
    path('export/thread-batches/', views.export_thread_batches, name='export_thread_batches'),
] 