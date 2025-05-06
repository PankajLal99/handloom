from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import timedelta
import csv
from .models import Weaver, Loom, ThreadBatch, ProductionLog, Inventory
from .forms import ThreadBatchForm, ProductionLogForm, LoomAssignmentForm, WeaverForm, LoomForm, InventoryForm
from .analytics import (
    get_weaver_performance_data,
    get_top_looms_data,
    get_production_trends_data,
    get_inventory_status_data,
    get_thread_utilization_data,
    get_low_production_alerts,
    get_thread_consumption_data,
    get_production_heatmap_data,
    get_loom_efficiency_data
)
from tracking.models import PageView, ScrollEvent, UserActivity

# Create your views here.

@login_required
def dashboard(request):
    """Dashboard view with key metrics and charts"""
    # Get monthly production
    today = timezone.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_production = ProductionLog.objects.filter(
        date__gte=month_start
    ).aggregate(total=Sum('meters_produced'))['total'] or 0
    
    # Round monthly production to 2 decimal places
    monthly_production = round(float(monthly_production), 2)
    
    # Get active weavers count
    active_weavers = Weaver.objects.filter(
        loom__status='active'
    ).distinct().count()
    
    # Get active looms count
    active_looms = Loom.objects.filter(status='active').count()
    
    # Get pending orders count
    pending_orders = ThreadBatch.objects.filter(
        status='pending',
        date__gte=today.date()
    ).count()
    
    # Get thread utilization data
    thread_batches = ThreadBatch.objects.all()
    total_thread = sum(batch.quantity_kg for batch in thread_batches)
    total_meters = sum(batch.get_utilization() for batch in thread_batches)
    avg_efficiency = sum(batch.get_efficiency() for batch in thread_batches) / len(thread_batches) if thread_batches else 0
    avg_meters_per_kg = total_meters / total_thread if total_thread > 0 else 0
    
    # Get top looms data for dashboard
    top_looms_data = Loom.objects.select_related('assigned_weaver').annotate(
        total_meters=Sum('productionlog__meters_produced')
    ).order_by('-total_meters')[:10]
    
    # Format top looms data for chart
    chart_data = {
        'labels': [loom.loom_id for loom in top_looms_data],
        'datasets': [{
            'label': 'Meters Produced',
            'data': [float(loom.total_meters or 0) for loom in top_looms_data],
            'backgroundColor': 'rgba(54, 162, 235, 0.5)',
            'borderColor': 'rgb(54, 162, 235)',
            'borderWidth': 1
        }]
    }
    
    # Get recent activities
    recent_activities = []
    
    # Add production logs
    for log in ProductionLog.objects.select_related('loom', 'thread_batch').order_by('-date')[:5]:
        recent_activities.append({
            'date': log.date,
            'type': 'Production',
            'details': f"{log.meters_produced} meters produced on Loom {log.loom.loom_id}"
        })
    
    # Add thread batch updates
    for batch in ThreadBatch.objects.order_by('-date')[:5]:
        recent_activities.append({
            'date': batch.date,
            'type': 'Thread Batch',
            'details': f"New batch {batch.batch_code} ({batch.color}) added"
        })
    
    # Add inventory updates
    for item in Inventory.objects.order_by('-last_updated')[:5]:
        recent_activities.append({
            'date': item.last_updated.date(),
            'type': 'Inventory',
            'details': f"{item.quantity} {item.unit} of {item.material_type} updated"
        })
    
    # Sort activities by date
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    recent_activities = recent_activities[:10]  # Keep only the 10 most recent
    
    context = {
        'monthly_production': monthly_production,
        'active_weavers': active_weavers,
        'active_looms': active_looms,
        'pending_orders': pending_orders,
        'thread_metrics': {
            'total_batches': len(thread_batches),
            'total_thread': round(float(total_thread), 2),
            'avg_efficiency': round(float(avg_efficiency), 1),
            'avg_meters_per_kg': round(float(avg_meters_per_kg), 2)
        },
        'recent_activities': recent_activities,
        'top_looms_data': chart_data  # Add top looms data to context
    }
    
    return render(request, 'supplychain/dashboard.html', context)

# Weaver Views
@login_required
def weaver_list(request):
    weavers = Weaver.objects.all()
    return render(request, 'supplychain/weaver_list.html', {'weavers': weavers})

@login_required
def weaver_create(request):
    if request.method == 'POST':
        form = WeaverForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Weaver created successfully.')
            return redirect('supplychain:weaver_list')
    else:
        form = WeaverForm()
    return render(request, 'supplychain/weaver_form.html', {'form': form})

@login_required
def weaver_detail(request, pk):
    weaver = get_object_or_404(Weaver, pk=pk)
    return render(request, 'supplychain/weaver_detail.html', {'weaver': weaver})

@login_required
def weaver_edit(request, pk):
    weaver = get_object_or_404(Weaver, pk=pk)
    if request.method == 'POST':
        form = WeaverForm(request.POST, instance=weaver)
        if form.is_valid():
            form.save()
            messages.success(request, 'Weaver updated successfully.')
            return redirect('supplychain:weaver_list')
    else:
        form = WeaverForm(instance=weaver)
    return render(request, 'supplychain/weaver_form.html', {'form': form})

@login_required
def weaver_delete(request, pk):
    weaver = get_object_or_404(Weaver, pk=pk)
    if request.method == 'POST':
        weaver.delete()
        messages.success(request, 'Weaver deleted successfully.')
        return redirect('supplychain:weaver_list')
    return render(request, 'supplychain/weaver_confirm_delete.html', {'weaver': weaver})

# Loom Views
@login_required
def loom_list(request):
    looms = Loom.objects.select_related('assigned_weaver').all()
    return render(request, 'supplychain/loom_list.html', {'looms': looms})

@login_required
def loom_create(request):
    if request.method == 'POST':
        form = LoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loom created successfully.')
            return redirect('supplychain:loom_list')
    else:
        form = LoomForm()
    return render(request, 'supplychain/loom_form.html', {'form': form})

@login_required
def loom_detail(request, loom_id):
    loom = get_object_or_404(Loom, loom_id=loom_id)
    return render(request, 'supplychain/loom_detail.html', {'loom': loom})

@login_required
def loom_edit(request, loom_id):
    loom = get_object_or_404(Loom, loom_id=loom_id)
    if request.method == 'POST':
        form = LoomForm(request.POST, instance=loom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loom updated successfully.')
            return redirect('supplychain:loom_list')
    else:
        form = LoomForm(instance=loom)
    return render(request, 'supplychain/loom_form.html', {'form': form})

@login_required
def loom_delete(request, loom_id):
    loom = get_object_or_404(Loom, loom_id=loom_id)
    if request.method == 'POST':
        loom.delete()
        messages.success(request, 'Loom deleted successfully.')
        return redirect('supplychain:loom_list')
    return render(request, 'supplychain/loom_confirm_delete.html', {'loom': loom})

@login_required
def loom_assignments(request):
    looms = Loom.objects.select_related('assigned_weaver').all()
    return render(request, 'supplychain/loom_assignments.html', {'looms': looms})

@login_required
def loom_assignment_edit(request, loom_id):
    loom = get_object_or_404(Loom, loom_id=loom_id)
    if request.method == 'POST':
        form = LoomAssignmentForm(request.POST, instance=loom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loom assignment updated successfully.')
            return redirect('supplychain:loom_assignments')
    else:
        form = LoomAssignmentForm(instance=loom)
    return render(request, 'supplychain/loom_assignment_form.html', {'form': form, 'loom': loom})

# Production Views
@login_required
def production_list(request):
    production_logs = ProductionLog.objects.select_related('loom', 'thread_batch').order_by('-date')
    return render(request, 'supplychain/production_log_list.html', {'production_logs': production_logs})

@login_required
def production_create(request):
    if request.method == 'POST':
        form = ProductionLogForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Production log created successfully.')
            return redirect('supplychain:production_list')
    else:
        form = ProductionLogForm()
    return render(request, 'supplychain/production_log_form.html', {'form': form})

@login_required
def production_detail(request, pk):
    production_log = get_object_or_404(ProductionLog, pk=pk)
    return render(request, 'supplychain/production_detail.html', {'production_log': production_log})

@login_required
def production_edit(request, pk):
    production_log = get_object_or_404(ProductionLog, pk=pk)
    if request.method == 'POST':
        form = ProductionLogForm(request.POST, instance=production_log)
        if form.is_valid():
            form.save()
            messages.success(request, 'Production log updated successfully.')
            return redirect('supplychain:production_list')
    else:
        form = ProductionLogForm(instance=production_log)
    return render(request, 'supplychain/production_form.html', {'form': form})

@login_required
def production_delete(request, pk):
    production_log = get_object_or_404(ProductionLog, pk=pk)
    if request.method == 'POST':
        production_log.delete()
        messages.success(request, 'Production log deleted successfully.')
        return redirect('supplychain:production_list')
    return render(request, 'supplychain/production_confirm_delete.html', {'production_log': production_log})

# Thread Batch Views
@login_required
def thread_batch_list(request):
    thread_batches = ThreadBatch.objects.all().order_by('-date')
    return render(request, 'supplychain/thread_batch_list.html', {'thread_batches': thread_batches})

@login_required
def thread_batch_create(request):
    if request.method == 'POST':
        form = ThreadBatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thread batch created successfully.')
            return redirect('supplychain:thread_batch_list')
    else:
        form = ThreadBatchForm()
    return render(request, 'supplychain/thread_batch_form.html', {'form': form})

@login_required
def thread_batch_detail(request, pk):
    thread_batch = get_object_or_404(ThreadBatch, pk=pk)
    return render(request, 'supplychain/thread_batch_detail.html', {'thread_batch': thread_batch})

@login_required
def thread_batch_edit(request, pk):
    thread_batch = get_object_or_404(ThreadBatch, pk=pk)
    if request.method == 'POST':
        form = ThreadBatchForm(request.POST, instance=thread_batch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thread batch updated successfully.')
            return redirect('supplychain:thread_batch_list')
    else:
        form = ThreadBatchForm(instance=thread_batch)
    return render(request, 'supplychain/thread_batch_form.html', {'form': form})

@login_required
def thread_batch_delete(request, pk):
    thread_batch = get_object_or_404(ThreadBatch, pk=pk)
    if request.method == 'POST':
        thread_batch.delete()
        messages.success(request, 'Thread batch deleted successfully.')
        return redirect('supplychain:thread_batch_list')
    return render(request, 'supplychain/thread_batch_confirm_delete.html', {'thread_batch': thread_batch})

# Inventory Views
@login_required
def inventory_list(request):
    inventory_items = Inventory.objects.all().order_by('material_type')
    return render(request, 'supplychain/inventory_list.html', {'inventory_items': inventory_items})

@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory item created successfully.')
            return redirect('supplychain:inventory_list')
    else:
        form = InventoryForm()
    return render(request, 'supplychain/inventory_form.html', {'form': form})

@login_required
def inventory_detail(request, pk):
    inventory_item = get_object_or_404(Inventory, pk=pk)
    return render(request, 'supplychain/inventory_detail.html', {'inventory_item': inventory_item})

@login_required
def inventory_edit(request, pk):
    inventory_item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory item updated successfully.')
            return redirect('supplychain:inventory_list')
    else:
        form = InventoryForm(instance=inventory_item)
    return render(request, 'supplychain/inventory_form.html', {'form': form})

@login_required
def inventory_delete(request, pk):
    inventory_item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        inventory_item.delete()
        messages.success(request, 'Inventory item deleted successfully.')
        return redirect('supplychain:inventory_list')
    return render(request, 'supplychain/inventory_confirm_delete.html', {'inventory_item': inventory_item})

# Analytics Views
@login_required
def weaver_performance(request):
    """View for weaver performance analytics"""
    # Get weaver data for the table
    weavers = Weaver.objects.annotate(
        total_production=Sum('loom__productionlog__meters_produced'),
        active_days=Count('loom__productionlog__date', distinct=True),
        avg_daily_production=Avg('loom__productionlog__meters_produced')
    ).all()

    # Calculate efficiency for each weaver
    for weaver in weavers:
        if weaver.active_days > 0:
            weaver.efficiency = (weaver.total_production or 0) / (weaver.active_days * 100) * 100  # Assuming 100m is daily target
        else:
            weaver.efficiency = 0

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        days = int(request.GET.get('days', 30))
        data = get_weaver_performance_data(days)
        return JsonResponse(data)

    # For initial page load, get chart data
    chart_data = get_weaver_performance_data(30)  # Get last 30 days data

    return render(request, 'supplychain/weaver_performance.html', {
        'weavers': weavers,
        'chart_data': chart_data
    })

@login_required
def top_looms(request):
    """View for top productive looms"""
    # Get top looms with their production data
    top_looms = Loom.objects.select_related('assigned_weaver').annotate(
        total_meters=Sum('productionlog__meters_produced')
    ).order_by('-total_meters')[:10]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = get_top_looms_data()
        return JsonResponse(data)
    return render(request, 'supplychain/top_looms.html', {
        'top_looms': top_looms,
        'chart_data': get_top_looms_data()  # Initial chart data
    })

@login_required
def production_trends(request):
    """View for production trends"""
    # Get daily production data for the table
    daily_production = ProductionLog.objects.values('date').annotate(
        total_meters=Sum('meters_produced'),
        active_looms=Count('loom', distinct=True),
        active_weavers=Count('loom__assigned_weaver', distinct=True),
        thread_used=Sum('thread_batch__quantity_kg')
    ).order_by('-date')[:30]

    # Calculate average production per loom
    for day in daily_production:
        day['avg_production'] = day['total_meters'] / day['active_looms'] if day['active_looms'] > 0 else 0

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        days = int(request.GET.get('days', 30))
        data = get_production_trends_data(days)
        return JsonResponse(data)
    return render(request, 'supplychain/production_trends.html', {
        'daily_production': daily_production,
        'chart_data': get_production_trends_data(30)  # Initial chart data
    })

@login_required
def inventory_status(request):
    """View for inventory status"""
    data = get_inventory_status_data()
    return render(request, 'supplychain/inventory_status.html', data)

@login_required
def thread_utilization(request):
    """View for thread utilization"""
    thread_batches = ThreadBatch.objects.all().order_by('-date')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = get_thread_utilization_data()
        return JsonResponse(data)
    return render(request, 'supplychain/thread_utilization.html', {
        'thread_batches': thread_batches,
        'chart_data': get_thread_utilization_data()  # Initial chart data
    })

@login_required
def low_production_alerts(request):
    """View for low production alerts"""
    threshold = float(request.GET.get('threshold', 10))
    alerts = get_low_production_alerts(threshold)
    return render(request, 'supplychain/low_production_alerts.html', {
        'alerts': alerts,
        'threshold': threshold
    })

@login_required
def thread_consumption_report(request):
    """View for thread consumption report"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    data = get_thread_consumption_data(start_date, end_date)
    return render(request, 'supplychain/thread_consumption_report.html', data)

@login_required
def production_heatmap(request):
    """View for production heatmap"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        days = int(request.GET.get('days', 30))
        data = get_production_heatmap_data(days)
        return JsonResponse(data)
    return render(request, 'supplychain/production_heatmap.html')

@login_required
def loom_efficiency(request):
    """View for loom efficiency report"""
    data = get_loom_efficiency_data()
    return render(request, 'supplychain/loom_efficiency.html', data)

# Export Views
@login_required
def export_production_logs(request):
    """Export production logs to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="production_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Loom ID', 'Thread Batch', 'Meters Produced', 'Issues'])
    
    logs = ProductionLog.objects.select_related('loom', 'thread_batch').all()
    for log in logs:
        writer.writerow([
            log.date,
            log.loom.loom_id,
            log.thread_batch.batch_code,
            log.meters_produced,
            log.issues_reported
        ])
    
    return response

@login_required
def export_thread_batches(request):
    """Export thread batches to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="thread_batches.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Batch Code', 'Date', 'Color', 'Quantity (kg)', 'Meters Produced', 'Efficiency'])
    
    batches = ThreadBatch.objects.all()
    for batch in batches:
        utilization = batch.get_utilization()
        efficiency = batch.get_efficiency()
        writer.writerow([
            batch.batch_code,
            batch.date,
            batch.color,
            batch.quantity_kg,
            utilization,
            efficiency
        ])
    
    return response

@login_required
def tracking_analytics(request):
    """View for tracking analytics"""
    # Get time range
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get page views
    page_views = PageView.objects.filter(
        timestamp__gte=start_date
    ).values('path').annotate(
        view_count=Count('id')
    ).order_by('-view_count')[:10]
    
    # Get scroll events
    scroll_events = ScrollEvent.objects.filter(
        timestamp__gte=start_date
    ).values('page_view__path').annotate(
        avg_scroll=Avg('scroll_position'),
        event_count=Count('id')
    ).order_by('-event_count')[:10]
    
    # Get user activity
    user_activity = UserActivity.objects.filter(
        timestamp__gte=start_date
    ).values('activity_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get daily page views
    daily_views = PageView.objects.filter(
        timestamp__gte=start_date
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    context = {
        'page_views': page_views,
        'scroll_events': scroll_events,
        'user_activity': user_activity,
        'daily_views': daily_views,
        'days': days
    }
    
    return render(request, 'supplychain/tracking_analytics.html', context)
