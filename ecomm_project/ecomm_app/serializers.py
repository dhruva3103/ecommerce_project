from datetime import datetime

from django.utils import timezone
from rest_framework import serializers
from .models import Customer, Product, Order, OrderItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'contact_number', 'email']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'weight']
        read_only_fields = ['id']

    def validate_weight(self, value):
        if value < 0 or value > 25:
            raise serializers.ValidationError("Weight must be a positive decimal not exceeding 25kg.")
        return value


class CustomDateField(serializers.Field):
    def to_representation(self, value):
        return value.strftime('%d/%m/%Y')

    def to_internal_value(self, data):
        try:
            return datetime.strptime(data, '%d/%m/%Y').date()
        except ValueError:
            raise serializers.ValidationError("Invalid date format. Please use 'dd/mm/yyyy'.")


class OrderItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']
        # read_only = True


class OrderSerializer(serializers.ModelSerializer):
    order_item = OrderItemSerializer(many=True)
    order_date = CustomDateField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'customer', 'order_date', 'address', 'order_item']
        # read_only_fields = ['id']

    def check_order_cumulative_weight(self, order_items_data):
        cumulative_weight = 0
        product_qty = dict()
        product_weight = dict()

        for item in order_items_data:
            if item['product'] not in product_qty:
                product_qty[str(item['product'])] = item['quantity']
            else:
                product_qty[str(item['product'])] += item['quantity']

        product_weight_query = Product.objects.filter(name__in=product_qty.keys()).values('name', 'weight').all()

        for record in product_weight_query:
            product_weight[record['name']] = record['weight']

        for product, qty in product_qty.items():
            cumulative_weight += (qty * product_weight[product])

        if cumulative_weight > 150:
            raise serializers.ValidationError("Order cumulative weight must be under 150kg")

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_item')

        self.check_order_cumulative_weight(order_items_data=order_items_data)

        if not validated_data.get('order_number', None):
            last_invoice = Order.objects.all().order_by("id").last()
            last_pk = 0
            if last_invoice:
                last_pk = last_invoice.pk
            validated_data['order_number'] = "ORD" + str(last_pk + 1).zfill(5)

        order = Order.objects.create(**validated_data)
        for order_item_data in order_items_data:
            OrderItem.objects.create(**order_item_data, order=order)
        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('order_item')
        self.check_order_cumulative_weight(order_items_data=order_items_data)

        # Update Order instance
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        # Track the existing OrderItem instances
        existing_order_items = {item['id']: item for item in instance.order_item.values()}

        # Update or create OrderItem instances
        for order_item_data in order_items_data:
            order_item_id = order_item_data.get('id')
            product_data = order_item_data.get('product', {})

            if order_item_id:
                # Update existing OrderItem
                existing_item = existing_order_items.pop(order_item_id, None)
                if existing_item:
                    existing_item['product_id'] = order_item_data['product']
                    existing_item['quantity'] = order_item_data['quantity']
                    OrderItem.objects.filter(id=order_item_id).update(**existing_item)
            else:
                # Create new OrderItem
                product = Product.objects.get(name=product_data)
                OrderItem.objects.create(order=instance, product=product, quantity=order_item_data['quantity'])

        # Delete any remaining OrderItem instances
        OrderItem.objects.filter(id__in=existing_order_items.keys()).delete()

        return instance

    def validate_order_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Order date cannot be in the past.")
        return value
