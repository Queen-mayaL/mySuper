import json
from django.db import connection
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Category, Customer, Employee, Supplier, Product, Order, OrderDetail, Payment
from .serializers import (
    CategorySerializer, CustomerSerializer, EmployeeSerializer, SupplierSerializer,
    ProductSerializer, OrderSerializer, OrderDetailSerializer, PaymentSerializer, NewOrderSerializer
)

from django.views.decorators.csrf import csrf_exempt

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
 
        # Add custom claims
        token['user_id'] = user.id
        token['username'] = user.username
        # token['is_superuser'] = user.is_superuser
        # token['is_staff'] = user.is_staff 
 
        return token
 
 
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAuthenticated]  # Restrict access

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_products_by_category(request, category_id):
    products = Product.objects.filter(category_id=category_id)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def register(request):
    user = User.objects.create_user(
                username=request.data['username'],
                password=request.data['password']
            )
    user.is_active = True
    user.is_staff = True
    user.save()
    return Response("new user born")

@api_view(['POST'])
def add_new_order(request):
    serializer = NewOrderSerializer(data=request.data)
    if serializer.is_valid():
        customer_id = serializer.validated_data['customer_id']
        order_details = serializer.validated_data['order_details']
        order_details_clean = [
            {
                "product_id": detail.get("product_id"),
                "quantity": detail.get("quantity"),
                "unit_price": float(detail.get("unit_price")),
            }
            for detail in order_details
        ]
        
        try:
            order_details_json = json.dumps(order_details_clean)
        except TypeError as e:
            return Response({"error": "Failed to serialize data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        try:
            with connection.cursor() as cursor:
                cursor.callproc('AddNewOrder', [customer_id, order_details_json])
            return Response({"message": "Order created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def call_update_user_interested(customer_id, product_id, quantity):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('update_user_interested', [customer_id, product_id, quantity])
    except Exception as e:
        return JsonResponse({"error": f"Failed to update user interest: {str(e)}"}, status=500)
    return None

@api_view(['POST'])
def add_to_cart(request):

    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated"}, status=401)

    customer_id = request.user.id

    products = request.data.get('products', [])

    if not isinstance(products, list) or not products:
        return JsonResponse({"error": "Invalid data format. Expected a list of products."}, status=400)

    for product in products:
        product_id = product.get('product_id')
        quantity = product.get('quantity')

        if product_id is None or quantity is None:
            return JsonResponse({"error": "Each product must have 'product_id' and 'quantity'."}, status=400)

        result = call_update_user_interested(customer_id, product_id, quantity)

        if result is not None:
            return result

    return JsonResponse({"message": "Products added to cart successfully."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_top_5_user_interests(request):
    customer_id = request.user.id

    try:
        with connection.cursor() as cursor:
            cursor.callproc('GetTop5UserInterests4', [customer_id])
            result = cursor.fetchall()

        product_ids = [row[0] for row in result]

        if not product_ids:
            return JsonResponse({"top_products": []}, status=200)

        products = Product.objects.filter(id__in=product_ids)
        serialized_products = ProductSerializer(products, many=True).data

        return JsonResponse({"top_products": serialized_products}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)