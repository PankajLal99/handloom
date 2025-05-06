from django.utils import timezone
from .models import PageView, UserActivity
import json
import re

class TrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        response = self.get_response(request)

        # Only track page views for GET requests
        if request.method == 'GET':
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            # Create page view
            page_view = PageView.objects.create(
                user=request.user if request.user.is_authenticated else None,
                path=request.path,
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT'),
                referrer=request.META.get('HTTP_REFERER'),
                session_id=request.session.session_key
            )

            # Log user activity
            if request.user.is_authenticated:
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='page_view',
                    details={
                        'path': request.path,
                        'method': request.method,
                        'user_agent': request.META.get('HTTP_USER_AGENT'),
                        'referrer': request.META.get('HTTP_REFERER')
                    },
                    ip_address=ip
                )

            # Add page view ID to HTML response
            if 'text/html' in response.get('Content-Type', ''):
                content = response.content.decode('utf-8')
                # Replace the meta tag with the page view ID
                content = re.sub(
                    r'<meta name="page-view-id" content="[^"]*">',
                    f'<meta name="page-view-id" content="{page_view.id}">',
                    content
                )
                response.content = content.encode('utf-8')

        return response 