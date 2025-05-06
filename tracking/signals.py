from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.models import User
from .models import UserActivity
import json

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """Track user login"""
    UserActivity.objects.create(
        user=user,
        activity_type='login',
        details={
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT')
        },
        ip_address=request.META.get('REMOTE_ADDR')
    )

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """Track user logout"""
    UserActivity.objects.create(
        user=user,
        activity_type='logout',
        details={
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT')
        },
        ip_address=request.META.get('REMOTE_ADDR')
    )

@receiver(pre_save, sender=User)
def user_pre_save_handler(sender, instance, **kwargs):
    """Track user profile updates"""
    if instance.pk:  # Only for existing users
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.email != instance.email:
                UserActivity.objects.create(
                    user=instance,
                    activity_type='email_change',
                    details={
                        'old_email': old_instance.email,
                        'new_email': instance.email
                    }
                )
        except User.DoesNotExist:
            pass 