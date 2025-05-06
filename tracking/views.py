from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import PageView, ScrollEvent
import json

# Create your views here.

@csrf_exempt
@require_http_methods(["POST"])
def track_scroll(request):
    """Handle scroll event tracking"""
    try:
        data = json.loads(request.body)
        page_view_id = data.get('page_view_id')
        scroll_position = data.get('scroll_position')
        
        if not page_view_id or scroll_position is None:
            return JsonResponse({'error': 'Missing required data'}, status=400)
        
        # Get the page view
        try:
            page_view = PageView.objects.get(id=page_view_id)
        except PageView.DoesNotExist:
            return JsonResponse({'error': 'Invalid page view ID'}, status=400)
        
        # Create scroll event
        ScrollEvent.objects.create(
            page_view=page_view,
            scroll_position=scroll_position,
            element_id=data.get('element_id'),
            element_class=data.get('element_class'),
            element_type=data.get('element_type')
        )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
