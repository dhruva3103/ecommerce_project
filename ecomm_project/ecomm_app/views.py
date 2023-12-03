from django.shortcuts import render
from rest_framework import generics
from .models import Customer, Product
from .serializers import CustomerSerializer, ProductSerializer, Order, OrderSerializer


class CustomerListView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        products_param = self.request.query_params.get('products', None)
        customer_param = self.request.query_params.get('customer', None)

        if products_param:
            products = products_param.split(',')
            queryset = queryset.filter(order_item__product__name__in=products)

        if customer_param:
            queryset = queryset.filter(customer__name=customer_param)

        return queryset


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

