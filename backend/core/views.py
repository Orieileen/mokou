# core/views.py

from rest_framework import viewsets, permissions
from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    一个只读的API视图集，用于列出和检索商品类目。
    - 'list': 提供所有激活的类目列表。 (GET /api/v1/categories/)
    - 'retrieve': 提供单个类目的详细信息。 (GET /api/v1/categories/{id}/)
    
    使用 ReadOnlyModelViewSet 是因为通常前端用户只能查看类目，而不能创建或修改。
    """
    # 关键点：直接使用我们定义好的 active_objects 管理器！
    queryset = Category.active_objects.all()
    
    # 将此视图与上面的序列化器关联起来
    serializer_class = CategorySerializer
    
    # 设置权限，例如：必须是登录用户才能访问
    # permission_classes = [permissions.IsAuthenticated]