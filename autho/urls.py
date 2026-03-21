from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MerchantViewSet

app_name = 'autho'

router = DefaultRouter()
router.register(r'merchants', MerchantViewSet, basename='merchant')

urlpatterns = [
    path('', include(router.urls)),
]
