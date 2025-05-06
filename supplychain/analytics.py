from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Weaver, Loom, ThreadBatch, ProductionLog, Inventory

def get_weaver_performance_data(days=30):
    """Get weaver performance data for charts"""
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get all weavers with their production data
    weavers = Weaver.objects.all()
    
    # Get daily production for each weaver
    weaver_data = {}
    dates = set()
    
    # Generate consistent colors for each weaver
    colors = {
        'primary': 'rgb(78, 115, 223)',
        'success': 'rgb(28, 200, 138)',
        'warning': 'rgb(246, 194, 62)',
        'danger': 'rgb(231, 74, 59)',
        'info': 'rgb(54, 185, 204)',
        'secondary': 'rgb(133, 135, 150)',
        'purple': 'rgb(111, 66, 193)',
        'pink': 'rgb(231, 74, 159)',
        'orange': 'rgb(253, 126, 20)',
        'teal': 'rgb(32, 201, 151)'
    }
    color_keys = list(colors.keys())
    
    for i, weaver in enumerate(weavers):
        daily_production = ProductionLog.objects.filter(
            loom__assigned_weaver=weaver,
            date__range=[start_date, end_date]
        ).values('date').annotate(
            total=Sum('meters_produced')
        ).order_by('date')
        
        dates.update([entry['date'].strftime('%Y-%m-%d') for entry in daily_production])
        weaver_data[weaver.name] = {
            'data': [entry['total'] or 0 for entry in daily_production],
            'dates': [entry['date'].strftime('%Y-%m-%d') for entry in daily_production],
            'color': colors[color_keys[i % len(color_keys)]]
        }

    # Sort dates
    dates = sorted(list(dates))

    # Calculate efficiency for each weaver
    weaver_efficiency = []
    for weaver in weavers:
        total_production = sum(weaver_data[weaver.name]['data'])
        active_days = len(set(weaver_data[weaver.name]['dates']))
        efficiency = (total_production / (active_days * 100) * 100) if active_days > 0 else 0
        weaver_efficiency.append(round(efficiency, 1))

    # Prepare chart data
    chart_data = {
        'labels': dates,
        'datasets': [
            {
                'label': weaver_name,
                'data': [weaver_data[weaver_name]['data'][weaver_data[weaver_name]['dates'].index(date)] if date in weaver_data[weaver_name]['dates'] else 0 for date in dates],
                'borderColor': weaver_data[weaver_name]['color'],
                'backgroundColor': weaver_data[weaver_name]['color'].replace('rgb', 'rgba').replace(')', ', 0.1)'),
                'fill': False,
                'tension': 0.1
            }
            for weaver_name in weaver_data.keys()
        ],
        'weavers': [weaver.name for weaver in weavers],
        'efficiency': weaver_efficiency
    }

    return chart_data

def get_top_looms_data():
    """Get data for top productive looms"""
    # Get top 10 looms with their production data
    top_looms = Loom.objects.select_related('assigned_weaver').annotate(
        total_meters=Sum('productionlog__meters_produced')
    ).order_by('-total_meters')[:10]
    
    return {
        'labels': [loom.loom_id for loom in top_looms],
        'datasets': [{
            'label': 'Total Production (meters)',
            'data': [float(loom.total_meters or 0) for loom in top_looms],
            'backgroundColor': 'rgba(78, 115, 223, 0.5)',
            'borderColor': 'rgb(78, 115, 223)',
            'borderWidth': 1
        }]
    }

def get_production_trends_data(days=30):
    """Get production trends data for the specified number of days"""
    start_date = timezone.now() - timedelta(days=days)
    
    daily_production = ProductionLog.objects.filter(
        date__gte=start_date
    ).values('date').annotate(
        total_meters=Sum('meters_produced'),
        active_looms=Count('loom', distinct=True),
        active_weavers=Count('loom__assigned_weaver', distinct=True)
    ).order_by('date')
    
    return {
        'dates': [log['date'].strftime('%Y-%m-%d') for log in daily_production],
        'production': [float(log['total_meters'] or 0) for log in daily_production],
        'active_looms': [log['active_looms'] for log in daily_production],
        'active_weavers': [log['active_weavers'] for log in daily_production]
    }

def get_inventory_status_data():
    """Get inventory status data"""
    # Calculate total raw materials
    total_raw_materials = Inventory.objects.filter(
        material_type__in=['yarn', 'dye', 'chemical']
    ).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    # Calculate total finished products
    total_finished_products = Inventory.objects.filter(
        material_type='finished_product'
    ).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    # Calculate total inventory value
    total_value = Inventory.objects.aggregate(
        total=Sum('value')
    )['total'] or 0
    
    # Get detailed inventory items
    inventory_items = Inventory.objects.all().order_by('material_type')
    
    # Add status to each item
    for item in inventory_items:
        if item.quantity < item.minimum_quantity:
            item.status = 'low'
        elif item.quantity < item.minimum_quantity * Decimal('1.5'):
            item.status = 'medium'
        else:
            item.status = 'adequate'
    
    return {
        'total_raw_materials': float(total_raw_materials),
        'total_finished_products': float(total_finished_products),
        'total_value': float(total_value),
        'inventory_items': inventory_items
    }

def get_thread_utilization_data():
    """Get thread utilization data with detailed metrics"""
    thread_batches = ThreadBatch.objects.all().order_by('-date')
    
    # Calculate utilization and efficiency for each batch
    batch_data = []
    for batch in thread_batches:
        utilization = batch.get_utilization()
        efficiency = batch.get_efficiency()
        meters_per_kg = utilization / batch.quantity_kg if batch.quantity_kg > 0 else 0
        
        batch_data.append({
            'batch_code': batch.batch_code,
            'color': batch.color,
            'quantity_kg': float(batch.quantity_kg),
            'utilization': float(utilization),
            'efficiency': float(efficiency),
            'meters_per_kg': float(meters_per_kg)
        })
    
    # Sort batches by utilization for the bar chart
    sorted_batches = sorted(batch_data, key=lambda x: x['utilization'], reverse=True)
    
    return {
        'utilization_chart': {
            'labels': [batch['batch_code'] for batch in sorted_batches],
            'datasets': [{
                'label': 'Meters Produced',
                'data': [batch['utilization'] for batch in sorted_batches],
                'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                'borderColor': 'rgb(54, 162, 235)',
                'borderWidth': 1
            }]
        },
        'efficiency_chart': {
            'labels': [batch['batch_code'] for batch in sorted_batches],
            'datasets': [{
                'label': 'Efficiency (%)',
                'data': [batch['efficiency'] for batch in sorted_batches],
                'backgroundColor': 'rgba(75, 192, 192, 0.5)',
                'borderColor': 'rgb(75, 192, 192)',
                'borderWidth': 1
            }]
        },
        'summary': {
            'total_batches': len(batch_data),
            'total_thread': sum(batch['quantity_kg'] for batch in batch_data),
            'total_meters': sum(batch['utilization'] for batch in batch_data),
            'avg_efficiency': sum(batch['efficiency'] for batch in batch_data) / len(batch_data) if batch_data else 0,
            'avg_meters_per_kg': sum(batch['meters_per_kg'] for batch in batch_data) / len(batch_data) if batch_data else 0
        }
    }

def get_low_production_alerts(threshold=10):
    """Get low production alerts"""
    return ProductionLog.get_low_production_alerts(threshold)

def get_thread_consumption_data(start_date=None, end_date=None):
    """Get thread consumption data"""
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    thread_batches = ThreadBatch.objects.filter(
        date__range=[start_date, end_date]
    )
    
    total_batches = thread_batches.count()
    total_thread = thread_batches.aggregate(total=Sum('quantity_kg'))['total'] or 0
    total_meters = ProductionLog.objects.filter(
        thread_batch__in=thread_batches
    ).aggregate(total=Sum('meters_produced'))['total'] or 0
    
    efficiency = total_meters / float(total_thread) if total_thread > 0 else 0
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'total_batches': total_batches,
        'total_thread': total_thread,
        'total_meters': total_meters,
        'efficiency': efficiency
    }

def get_production_heatmap_data(days=30):
    """Get production heatmap data"""
    production_data = ProductionLog.get_daily_production(days)
    
    return {
        'dates': [item['date'].strftime('%Y-%m-%d') for item in production_data],
        'values': [float(item['total_meters']) for item in production_data]
    }

def get_loom_efficiency_data():
    """Get loom efficiency data"""
    looms = Loom.objects.all()
    efficiency_data = []
    
    for loom in looms:
        efficiency_data.append({
            'loom_id': loom.loom_id,
            'total_meters': loom.get_monthly_production(),
            'efficiency': loom.get_efficiency_ratio()
        })
    
    return {'efficiency_data': efficiency_data} 