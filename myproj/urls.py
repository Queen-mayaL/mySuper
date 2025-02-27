from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter  # ✅ Import this

# Import your ViewSets
from base.views import (
    CategoryViewSet, CustomerViewSet, EmployeeViewSet, SupplierViewSet,
    ProductViewSet, OrderViewSet, OrderDetailViewSet, PaymentViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-details', OrderDetailViewSet)
router.register(r'payments', PaymentViewSet)

# Define URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('base.urls')),
]
