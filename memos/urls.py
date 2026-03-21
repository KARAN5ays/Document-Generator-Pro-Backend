from django.urls import path, include
from rest_framework.routers import DefaultRouter
from memos.views import MemoViewSet

app_name = 'memos'

router = DefaultRouter()
router.register(r'memos', MemoViewSet, basename='memo')

urlpatterns = [
    path('', include(router.urls)),
]
