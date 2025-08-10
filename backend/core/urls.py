# core/urls.py
from rest_framework import routers
from .views import CategoryViewSet

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
urlpatterns = router.urls