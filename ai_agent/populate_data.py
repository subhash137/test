import os
import random
import decimal
from datetime import datetime, timedelta

# Setup Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_agent.settings')
django.setup()

from my_app.models import Supplier, Component, Laptop, Inventory, Order

# Helper function to generate random data
def random_date(start, end):
    """Generate a random date between two datetime objects."""
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

# Create Suppliers
def create_suppliers():
    countries = ['USA', 'China', 'Germany', 'Japan', 'India']
    suppliers = [
        Supplier(name=f"Supplier {i+1}", country=random.choice(countries), reliability_score=random.uniform(0.5, 5.0))
        for i in range(10)
    ]
    Supplier.objects.bulk_create(suppliers)

# Create Components
def create_components():
    suppliers = Supplier.objects.all()
    categories = ['CPU', 'RAM', 'SSD', 'SCREEN', 'GPU']
    components = [
        Component(
            name=f"Component {i+1}",
            category=random.choice(categories),
            supplier=random.choice(suppliers),
            price=decimal.Decimal(random.uniform(50, 500)).quantize(decimal.Decimal('0.01')),
            lead_time_days=random.randint(1, 30)
        )
        for i in range(50)
    ]
    Component.objects.bulk_create(components)

# Create Laptops
def create_laptops():
    components = list(Component.objects.all())
    laptops = []
    for i in range(20):
        selected_components = random.sample(components, random.randint(3, 5))
        production_cost = sum(component.price for component in selected_components)
        selling_price = production_cost * decimal.Decimal(random.uniform(1.2, 1.5))
        laptop = Laptop(
            model_name=f"Laptop Model {i+1}",
            production_date=random_date(datetime(2023, 1, 1), datetime(2024, 12, 1)),
            production_cost=production_cost.quantize(decimal.Decimal('0.01')),
            selling_price=selling_price.quantize(decimal.Decimal('0.01')),
            units_produced=random.randint(100, 1000)
        )
        laptops.append(laptop)
    Laptop.objects.bulk_create(laptops)

    # Add components to laptops
    for laptop in Laptop.objects.all():
        laptop.components.set(random.sample(components, random.randint(3, 5)))

# Create Inventory
def create_inventory():
    warehouses = ['Warehouse A', 'Warehouse B', 'Warehouse C']
    inventories = [
        Inventory(
            laptop=laptop,
            quantity=random.randint(10, 200),
            warehouse_location=random.choice(warehouses)
        )
        for laptop in Laptop.objects.all()
    ]
    Inventory.objects.bulk_create(inventories)

# Create Orders
def create_orders():
    laptops = Laptop.objects.all()
    statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED']
    orders = [
        Order(
            laptop=random.choice(laptops),
            quantity=random.randint(1, 50),
            status=random.choice(statuses),
            delivery_date=random_date(datetime(2023, 1, 1), datetime(2024, 12, 1)) if random.choice([True, False]) else None
        )
        for _ in range(100)
    ]
    Order.objects.bulk_create(orders)

# Main function to populate data
def main():
    create_suppliers()
    create_components()
    create_laptops()
    create_inventory()
    create_orders()
    print("Dummy data populated successfully!")

if __name__ == "__main__":
    main()

