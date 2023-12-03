from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(25)])

    def __str__(self):
        return self.name


def generate_order_number():
    last_order = Order.objects.all().order_by('id').last()
    if not last_order:
        return 'ORD00001'
    order_number = last_order.order_number
    order_int = int(order_number[3:]) + 1
    order_str = str(order_int).zfill(5)
    return f'ORD{order_str}'


class Order(models.Model):
    # order_number = models.CharField(max_length=10, unique=True, default=generate_order_number(), editable=False)
    order_number = models.CharField(max_length=10, unique=True, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField(default=timezone.now)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_item')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

