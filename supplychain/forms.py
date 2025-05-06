from django import forms
from .models import ThreadBatch, ProductionLog, Loom, Weaver, Inventory

class ThreadBatchForm(forms.ModelForm):
    class Meta:
        model = ThreadBatch
        fields = ['batch_code', 'date', 'color', 'quantity_kg']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'batch_code': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class ProductionLogForm(forms.ModelForm):
    class Meta:
        model = ProductionLog
        fields = ['date', 'loom', 'thread_batch', 'meters_produced', 'issues_reported']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'loom': forms.Select(attrs={'class': 'form-control'}),
            'thread_batch': forms.Select(attrs={'class': 'form-control'}),
            'meters_produced': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'issues_reported': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active looms in the dropdown
        self.fields['loom'].queryset = Loom.objects.filter(status='active')

class LoomAssignmentForm(forms.ModelForm):
    class Meta:
        model = Loom
        fields = ['assigned_weaver', 'status']
        widgets = {
            'assigned_weaver': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }

class WeaverForm(forms.ModelForm):
    class Meta:
        model = Weaver
        fields = ['name', 'contact', 'skill_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'skill_level': forms.Select(attrs={'class': 'form-control'})
        }

class LoomForm(forms.ModelForm):
    class Meta:
        model = Loom
        fields = ['loom_id', 'loom_type', 'assigned_weaver', 'status']
        widgets = {
            'loom_id': forms.TextInput(attrs={'class': 'form-control'}),
            'loom_type': forms.Select(attrs={'class': 'form-control'}),
            'assigned_weaver': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['material_type', 'name', 'quantity', 'unit', 'minimum_quantity', 'value', 'supplier']
        widgets = {
            'material_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'minimum_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'})
        } 