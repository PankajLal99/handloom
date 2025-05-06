from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Create your models here.

class Weaver(models.Model):
    SKILL_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    ]
    
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_skill_level_display()})"
    
    def get_daily_production(self, days=30):
        """Get daily production for the last N days"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        return ProductionLog.objects.filter(
            loom__assigned_weaver=self,
            date__range=[start_date, end_date]
        ).values('date').annotate(
            total_meters=Sum('meters_produced')
        ).order_by('date')
    
    def get_monthly_efficiency(self):
        """Calculate efficiency (meters/kg) for current month"""
        start_date = timezone.now().date().replace(day=1)
        end_date = timezone.now().date()
        
        total_meters = ProductionLog.objects.filter(
            loom__assigned_weaver=self,
            date__range=[start_date, end_date]
        ).aggregate(total=Sum('meters_produced'))['total'] or 0
        
        total_thread = ThreadBatch.objects.filter(
            productionlog__loom__assigned_weaver=self,
            productionlog__date__range=[start_date, end_date]
        ).aggregate(total=Sum('quantity_kg'))['total'] or 0
        
        return total_meters / total_thread if total_thread > 0 else 0

class Loom(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
    ]
    
    LOOM_TYPE_CHOICES = [
        ('traditional', 'Traditional'),
        ('semi-automatic', 'Semi-Automatic'),
        ('automatic', 'Automatic'),
    ]
    
    loom_id = models.CharField(max_length=20, unique=True)
    loom_type = models.CharField(max_length=20, choices=LOOM_TYPE_CHOICES, default='traditional')
    assigned_weaver = models.ForeignKey(Weaver, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loom {self.loom_id} - {self.get_status_display()}"
    
    def get_monthly_production(self):
        """Get total production for current month"""
        start_date = timezone.now().date().replace(day=1)
        end_date = timezone.now().date()
        return ProductionLog.objects.filter(
            loom=self,
            date__range=[start_date, end_date]
        ).aggregate(total=Sum('meters_produced'))['total'] or 0
    
    def get_efficiency_ratio(self):
        """Calculate efficiency ratio (meters/kg)"""
        total_meters = ProductionLog.objects.filter(loom=self).aggregate(
            total=Sum('meters_produced')
        )['total'] or 0
        
        total_thread = ThreadBatch.objects.filter(
            productionlog__loom=self
        ).aggregate(total=Sum('quantity_kg'))['total'] or 0
        
        return total_meters / total_thread if total_thread > 0 else 0

class ThreadBatch(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_production', 'In Production'),
        ('completed', 'Completed'),
    ]
    batch_code = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    color = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Batch {self.batch_code} - {self.color} ({self.quantity_kg}kg)"
    
    def get_utilization(self):
        """Get total meters produced from this batch"""
        return ProductionLog.objects.filter(
            thread_batch=self
        ).aggregate(total=Sum('meters_produced'))['total'] or 0
    
    def get_efficiency(self):
        """Calculate efficiency (meters/kg)"""
        total_meters = self.get_utilization()
        return (total_meters / self.quantity_kg * 100) if self.quantity_kg > 0 else 0
    
    def get_meters_per_kg(self):
        """Calculate meters per kg"""
        return self.quantity_kg / self.get_utilization() if self.get_utilization() > 0 else 0

class ProductionLog(models.Model):
    date = models.DateField()
    loom = models.ForeignKey(Loom, on_delete=models.CASCADE)
    thread_batch = models.ForeignKey(ThreadBatch, on_delete=models.CASCADE)
    meters_produced = models.DecimalField(max_digits=10, decimal_places=2)
    issues_reported = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Production Log - {self.date} - Loom {self.loom.loom_id}"
    
    @classmethod
    def get_daily_production(cls, days=30):
        """Get daily production totals for all looms"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        return cls.objects.filter(
            date__range=[start_date, end_date]
        ).values('date').annotate(
            total_meters=Sum('meters_produced')
        ).order_by('date')
    
    @classmethod
    def get_low_production_alerts(cls, threshold=10):
        """Get production logs below threshold"""
        return cls.objects.filter(
            meters_produced__lt=threshold
        ).select_related('loom', 'loom__assigned_weaver', 'thread_batch')

class Inventory(models.Model):
    MATERIAL_TYPES = [
        ('yarn', 'Yarn'),
        ('dye', 'Dye'),
        ('chemical', 'Chemical'),
        ('finished_product', 'Finished Product'),
    ]
    
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)  # kg, meters, liters, etc.
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    value = models.DecimalField(max_digits=10, decimal_places=2)  # Value in currency
    supplier = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Inventory"
        ordering = ['material_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_material_type_display()}) - {self.quantity} {self.unit}"
    
    def get_status(self):
        """Get inventory status based on quantity"""
        if self.quantity < self.minimum_quantity:
            return 'low'
        elif self.quantity < self.minimum_quantity * Decimal('1.5'):
            return 'medium'
        return 'adequate'
