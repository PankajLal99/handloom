from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from supplychain.models import Weaver, Loom, ThreadBatch, ProductionLog, Inventory
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Generates sample data for the handloom supply chain'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating sample data...')

        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Created admin user')

        # Generate Weavers
        weaver_names = [
            'Rajesh Kumar', 'Priya Sharma', 'Amit Patel', 'Sneha Gupta', 'Vikram Singh',
            'Meera Joshi', 'Rahul Verma', 'Anita Desai', 'Kiran Reddy', 'Suresh Iyer'
        ]
        weavers = []
        for name in weaver_names:
            weaver = Weaver.objects.create(
                name=name,
                contact=f'+91{random.randint(7000000000, 9999999999)}',
                skill_level=random.choice(['beginner', 'intermediate', 'expert'])
            )
            weavers.append(weaver)
        self.stdout.write(f'Created {len(weavers)} weavers')

        # Generate Looms
        statuses = ['active', 'maintenance', 'inactive']
        loom_types = ['traditional', 'semi-automatic', 'automatic']
        looms = []
        for i in range(50):  # 50 looms
            loom = Loom.objects.create(
                loom_id=f'LOOM{i+1:03d}',
                loom_type=random.choice(loom_types),
                assigned_weaver=random.choice(weavers) if random.random() > 0.2 else None,
                status=random.choice(statuses)
            )
            looms.append(loom)
        self.stdout.write(f'Created {len(looms)} looms')

        # Generate Thread Batches
        colors = ['red', 'blue', 'green', 'yellow', 'black', 'white', 'purple', 'orange']
        statuses = ['pending', 'in_production', 'completed']
        thread_batches = []
        for i in range(2000):  # 2000 thread batches
            batch = ThreadBatch.objects.create(
                batch_code=f'TB{i+1:04d}',
                date=timezone.now() - timedelta(days=random.randint(0, 365)),
                color=random.choice(colors),
                quantity_kg=random.uniform(1.0, 50.0),
                status=random.choice(statuses),
                created_by=User.objects.get(username='admin')
            )
            thread_batches.append(batch)
        self.stdout.write(f'Created {len(thread_batches)} thread batches')

        # Generate Production Logs
        for i in range(2000):  # 2000 production logs
            active_loom = random.choice([l for l in looms if l.status == 'active'])
            ProductionLog.objects.create(
                date=timezone.now() - timedelta(days=random.randint(0, 365)),
                loom=active_loom,
                thread_batch=random.choice(thread_batches),
                meters_produced=random.uniform(1.0, 100.0),
                issues_reported=random.choice(['', 'Thread break', 'Quality issue', 'Machine problem']),
                created_by=User.objects.get(username='admin')
            )
        self.stdout.write(f'Created 2000 production logs')

        # Generate Inventory Items
        # Yarn inventory
        yarn_types = ['Cotton', 'Silk', 'Wool', 'Synthetic', 'Blend']
        for yarn in yarn_types:
            Inventory.objects.create(
                material_type='yarn',
                name=f'{yarn} Yarn',
                quantity=random.uniform(100.0, 1000.0),
                unit='kg',
                minimum_quantity=200.0,
                value=random.uniform(1000.0, 10000.0),
                supplier=random.choice(['ABC Textiles', 'XYZ Yarns', 'PQR Fibers'])
            )

        # Dye inventory
        dye_colors = ['Red', 'Blue', 'Green', 'Yellow', 'Black', 'White']
        for color in dye_colors:
            Inventory.objects.create(
                material_type='dye',
                name=f'{color} Dye',
                quantity=random.uniform(10.0, 100.0),
                unit='liters',
                minimum_quantity=20.0,
                value=random.uniform(500.0, 5000.0),
                supplier=random.choice(['ColorChem', 'DyeMasters', 'ColorWorld'])
            )

        # Chemical inventory
        chemicals = ['Bleach', 'Softener', 'Starch', 'Sizing Agent']
        for chemical in chemicals:
            Inventory.objects.create(
                material_type='chemical',
                name=chemical,
                quantity=random.uniform(50.0, 200.0),
                unit='kg',
                minimum_quantity=50.0,
                value=random.uniform(1000.0, 5000.0),
                supplier=random.choice(['ChemCorp', 'Industrial Chemicals', 'TextileChem'])
            )

        # Finished products
        product_types = ['Saree', 'Dress Material', 'Shirt Material', 'Curtain Fabric']
        for product in product_types:
            Inventory.objects.create(
                material_type='finished_product',
                name=product,
                quantity=random.uniform(100.0, 500.0),
                unit='meters',
                minimum_quantity=100.0,
                value=random.uniform(5000.0, 25000.0),
                supplier='Internal Production'
            )

        self.stdout.write('Created inventory items')
        self.stdout.write(self.style.SUCCESS('Successfully generated sample data')) 