from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PageView(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.path} - {self.timestamp}"

class ScrollEvent(models.Model):
    page_view = models.ForeignKey(PageView, on_delete=models.CASCADE, related_name='scroll_events')
    scroll_position = models.IntegerField()  # Scroll position in pixels
    timestamp = models.DateTimeField(default=timezone.now)
    element_id = models.CharField(max_length=255, null=True, blank=True)
    element_class = models.CharField(max_length=255, null=True, blank=True)
    element_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Scroll to {self.scroll_position}px at {self.timestamp}"

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    activity_type = models.CharField(max_length=50)  # e.g., 'login', 'logout', 'page_view'
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'User Activities'

    def __str__(self):
        return f"{self.activity_type} - {self.timestamp}"
